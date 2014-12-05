from zch_logger import setup
log_env = setup()
log_env.push_application()

from wowhua_admin.config import get_config
from wowhua_admin.wsgi_application import application


def start():
    setting = get_config()

    # start HTTP server
    http_port = setting['port']
    debug = setting['debug']

    application.debug = debug
    application.run('0.0.0.0', port=http_port)
