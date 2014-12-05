#!usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import gevent
import math
import random
from gsm.proxy import GameProxy
from sallyconf.config import Config
from wowhua_admin.log import logger
from wowhua_db.aux.models import TempWonTicketMapper
from tinyrpc import RPCClient
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport
from wowhua_db.api.models import TicketMapper, PrizeMapper
from wowhua_db.api.util import scoped_session as _api_session
from wowhua_db.aux.util import scoped_session as _aux_session
from wowhua_db.admin.models import LotteryMapper, ProviderLotteryMapper
from wowhua_db.admin.util import scoped_session as _admin_session
from wowhua_db.model_utils.game import set_game_default_prize
from wowhua_db.common.util import bonus_code_validator
from wowhua_db.common.constants import (
    game_result_status, game_result_type, ticket_process_status,
    ticket_bonus_results, game_status)
from wowhua_db.common.constants import (
    ticket_providers as ticket_providers_enum)
from wowhua_admin.errors import ResultingError
from zk.client import ZKClient
from ticket_job.protocol import ResultingProtocol
from gevent import spawn, joinall


_config = Config('wowhua_admin')
_resulting_config = _config['RESULTING_SERVICE']


def _get_resulting_service(name_service=None, debug=None):
    if debug is None:
        debug = _config['debug']
    if debug:
        endpoints = ['127.0.0.1:9002']
    else:
        name_service = name_service or ZKClient().NameService()
        endpoints = name_service.query(
            _resulting_config['name'],
            _resulting_config['major_version'],
            _resulting_config['minor_version']
        )
    instances = [
        RPCClient(
            JSONRPCProtocol(),
            HttpPostClientTransport('http://{}/'.format(endpoint))
        ).get_proxy() for endpoint in endpoints
    ]
    return random.choice(instances)


def _get_game(game_id):
    game = GameProxy.load_game_protocol_by_id(game_id)
    if not game:
        raise ResultingError('game {} not found'.format(game_id))
    return game


def _set_game(game):
    GameProxy.set_game_protocol(game.lottery_code, game.issue, game, force=True)
    game.dump_db()


def _get_prize_detail(game_id, api_session):
    rows = api_session.query(PrizeMapper.category, PrizeMapper.payment).filter(
        PrizeMapper.game_id == game_id).all()
    return {str(row[0]): row[1] for row in rows}


def _check_resulting_enabled(lottery_code, admin_session):
    lottery = admin_session.query(
        LotteryMapper).filter_by(code=lottery_code).one()
    if lottery.result_type != game_result_type.CALCULATE:
        raise ResultingError(
            'resulting type of lottery "{}" is not CALCULATE!'.format(
                game_result_type[lottery.result_type]
            ))


def _check_status(game, status_name, expected, msg=''):
    if not getattr(game, status_name) in expected:
        raise ResultingError(
            'invalid {status_name} "{got}", {expected} expected; {}'.format(
                msg, status_name=status_name, got=getattr(game, status_name),
                expected=expected,
            ))


def _get_tickets_total(game_id, api_session):
    return api_session.query(TicketMapper.id).filter_by(
        game_id=game_id, process_status=ticket_process_status.SUCCEEDED,
        bonus_result=ticket_bonus_results.WAITING
    ).count()


def _remove_temp_won_tickets(game_id, aux_session):
    aux_session.query(TempWonTicketMapper).delete(synchronize_session=False)
    aux_session.commit()


def _result_tickets(
        result_service, game, prize_detail, batch_id,
        total_batches):
    f = getattr(result_service, 'result_{}'.format(game.lottery_code))
    return f(game.bonus_code, prize_detail, game.id, batch_id, total_batches)


def check_resulting_condition(
        game_id, admin_session=_admin_session, api_session=_api_session):
    """
    Check if the game can be resulted
    :return: game and prize_detail if the check passes
    :raises:
        :exc:`~wowhua_admin.errors.ResultingError`. Check its `message`
        attribute for failure reason
    """
    game = _get_game(game_id)
    # validation
    # admin.lottery.result_type should be CALCULATE
    _check_resulting_enabled(game.lottery_code, admin_session)
    if game.resulting_status is None:
        # for backward compatibility
        game.resulting_status = game_result_status.WAITING
        _set_game(game)
    _check_status(game, 'resulting_status',
                  (game_result_status.WAITING, game_result_status.FAILED),
                  'cannot start resulting')
    _check_status(game, 'status', (
        game_status.STOP_BET, game_status.RESULTING), 'cannot start resulting')
    try:
        ok = bonus_code_validator(game.bonus_code, game.lottery_code)
    except:
        ok = False
    if not ok:
        raise ResultingError('invalid bonus code for game {}'.format(
            game_id))

    # prepare resulting data
    prize_detail = _get_prize_detail(game_id, api_session)
    if not prize_detail:
        # for backward compatibility
        set_game_default_prize(game)
        _set_game(game)
        prize_detail = {p.category: p.payment for p in game.prize_list}
    for category, payment in prize_detail.items():
        if payment:
            prize_detail[category] = float(payment)
        else:
            raise ResultingError(
                'prize detail incomplete for game {}: no payment for ' +
                'category {}'.format(game_id, category))
    return game, prize_detail


def result_tickets(game_id, api_session=_api_session,
                   admin_session=_admin_session, aux_session=_aux_session,
                   name_service=None):
    """
    result tickets in a game

    :param game_id: specify game to result
    :param api_session: session obj to the api DB
    :param admin_session: session obj to the admin DB
    :param name_service: only used in tests

    :return: number of winning tickets
    :raises:
        :exc:`~wowhua_admin.errors.ResultingError`. Check its `message`
        attribute for failure reason
    """
    game, prize_detail = check_resulting_condition(
        game_id, admin_session, api_session)

    # start resulting

    if game.status == game_status.STOP_BET:
        game.status = game_status.RESULTING
    game.resulting_status = game_result_status.CALCULATING
    game.resulting_time = datetime.now()
    _set_game(game)
    _remove_temp_won_tickets(game_id, aux_session)
    total_tickets = _get_tickets_total(game_id, api_session)
    total_batches = int(math.ceil(
        total_tickets / float(_resulting_config['batch_size'])))

    # get resulting service
    greenlets = []

    for i in xrange(total_batches):
        service = _get_resulting_service(name_service)
        g = gevent.spawn(
            _result_tickets, service, game, prize_detail, i, total_batches)
        greenlets.append(g)
        gevent.sleep(0.1)

    try:
        gevent.joinall(greenlets, raise_error=True)
    except Exception as e:
        logger.error('fail to result tickets: {}', e)
        game.resulting_status = game_result_status.FAILED
        raise
    else:
        game.resulting_status = game_result_status.AUDITING
        r = {
            'total': sum(g.value['total'] for g in greenlets),
            'winning': sum(g.value['winning'] for g in greenlets)
        }
        if r['total'] != total_tickets:
            logger.warning(
                'total # of tickets({}) fetched != # of tickets resulted({})',
                total_tickets, r['total']
            )
        return r
    finally:
        _set_game(game)


def re_result_tickets(game_id):
    """
    set game result status so that it can be resulted again
    """
    game = _get_game(game_id)
    _check_status(game, 'resulting_status', [
        game_result_status.AUDITING
    ])
    game.resulting_status = game_result_status.WAITING
    _set_game(game)


def check_dispatch_prize_condition(game_id):
    """
    check if prizes in the game can be dispatched
    :param game_id: specify game to result
    :return: game object
    :raises:
        :exc:`~wowhua_admin.errors.ResultingError`. Check its `message`
        attribute for failure reason
    """
    game = _get_game(game_id)
    _check_status(game, 'status', [game_status.RESULTING],
                  'cannot dispatch prizes')
    _check_status(game, 'resulting_status', [game_result_status.AUDITING],
                  'cannot dispatch prizes')
    return game


def dispatch_prize(game_id, name_service=None):
    """
    dispatch prizes in a game
    :param game_id: specify game to result
    :return:
        a dict containing the number of tickets won and lose, like
        `{"winning": 10, "losing": 200012}`
    """
    game = check_dispatch_prize_condition(game_id)
    game.resulting_status = game_result_status.ACCEPTED
    _set_game(game)
    service = _get_resulting_service(name_service)
    try:
        resp = service.dispatch_prize(game_id=game_id)
    except Exception as e:
        game.result_status = game_result_status.FAILED
        logger.error('game %s fail to dispatch ticket prizes: %s', game_id, e)
        raise ResultingError(e.message)
    else:
        game.status = game_status.RESULTED
        game.resulting_status = game_result_status.SUCCEEDED
        game.resulted_time = datetime.now()
        return resp
    finally:
        _set_game(game)


def result_by_provider(game_id, admin_session=_admin_session):
    """
    Deny the prizes got by the resulting service. Use provider APIs to result
    the game.
    :param game_id:
    :return:
    """
    game = _get_game(game_id)
    _check_status(game, 'resulting_status', [
        game_result_status.AUDITING
    ])
    game.resulting_status = game_result_status.DENIED
    _set_game(game)
    # find all available providers for game
    results = admin_session.query(ProviderLotteryMapper).filter_by(
        lottery_code=game.lottery_code).all()
    provider_ids = [result.provider_id for result in results]
    provider_names = [ticket_providers_enum.getNamesDict()[provider_id]
                      for provider_id in provider_ids]

    # send resulting_jobs in parallel
    greenlets = []
    for provider_name in provider_names:
        g = spawn(send_provider_result_job, provider_name, game_id, game.issue,
                  game.lottery_code)
        greenlets.append(g)

    try:
        joinall(greenlets, raise_error=True)
    except Exception as e:
        logger.error('fail to send provider resulting job: {}', e)
        raise
    else:
        return True


def send_provider_result_job(provider_id, game_id, issue, lottery_code):
    job = ResultingProtocol(provider_id, game_id, issue, lottery_code)
    logger.info('prepare resulting job %s', job)
    try:
        job.send()
    except Exception:
        logger.exception('Error when putting job, resason')
        raise
    else:
        logger.info('put resulting job: %s', job)
