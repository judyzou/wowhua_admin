import copy
from flask import _app_ctx_stack
from flask.signals import Namespace
from sqlalchemy import orm
from sqlalchemy.event import listen
from wowhua_db.api.util import get_scoped_session as get_api_session
from wowhua_db.admin.util import get_scoped_session as get_admin_session

# migrated from flask_sqlalchemy
_signals = Namespace()
models_committed = _signals.signal('models-committed')

class SignallingSession(orm.Session):

    def __init__(self, **options):
        super(SignallingSession, self).__init__(**options)
        self._model_changes = {}


class _SessionSignalEvents(object):

    def register(self, app):
        self.app = app
        listen(SignallingSession, 'after_commit', self.session_signal_after_commit)

    def session_signal_after_commit(self, session):
        d = session._model_changes
        if d:
            models_committed.send(self.app, changes=d.values())
            d.clear()


class _MapperSignalEvents(object):

    def __init__(self):
        self.mapper = orm.mapper

    def register(self, app):
        listen(self.mapper, 'after_delete', self.mapper_signal_after_delete)
        listen(self.mapper, 'after_insert', self.mapper_signal_after_insert)
        listen(self.mapper, 'after_update', self.mapper_signal_after_update)
        listen(self.mapper, 'load', self.mapper_signal_load)

    def mapper_signal_after_delete(self, mapper, connection, target):
        self._record(mapper, target, 'delete')

    def mapper_signal_after_insert(self, mapper, connection, target):
        self._record(mapper, target, 'insert')

    def mapper_signal_after_update(self, mapper, connection, target):
        self._record(mapper, target, 'update')

    def mapper_signal_load(self, target, context):
        setattr(target, '__old_values__', copy.copy(target.__dict__))

    @staticmethod
    def _record(mapper, target, operation):
        table = getattr(mapper, 'mapped_table', str(mapper))
        s = orm.object_session(target)
        if isinstance(s, SignallingSession):
            pk = tuple(mapper.primary_key_from_instance(target))
            dpk = '%s(%s)' % (table, pk)
            old_values = getattr(target, '__old_values__', {})
            new_values = target.__dict__
            s._model_changes[dpk] = (table, old_values, new_values, operation)

scopefunc = _app_ctx_stack.__ident_func__
api_session = get_api_session(session_cls=SignallingSession, scopefunc=scopefunc)
admin_session = get_admin_session(session_cls=SignallingSession, scopefunc=scopefunc)

def session_init(app, on_models_committed):
    _SessionSignalEvents().register(app)
    _MapperSignalEvents().register(app)
    models_committed.connect(on_models_committed, sender=app)
