from sys import exc_info
from sallyconf.config import Config


dir_name = 'wowhua_admin'
config = Config(dir_name, extra_check=True)


def get_config():
    if config is None:
        #  init config from scratch
        error_info = exc_info()
        assert False, error_info
    return config
