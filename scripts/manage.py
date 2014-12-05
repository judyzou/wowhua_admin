from flask.ext.script import Manager
from flask import url_for

from wowhua_admin.wsgi_application import application as app
from wowhua_db.model_utils.data_util import drop_dbs, init_dbs

manager = Manager(app)

@manager.command
def reset_db():
    drop_dbs()
    init_dbs()



if __name__ == "__main__":
    manager.run()
