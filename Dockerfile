FROM python:2.7.8-onbuild

ENV hnwowhua_db_aux_db postgresql://zch@wowhua_postgres/wowhua_aux
ENV hnwowhua_db_api_db postgresql://zch@wowhua_postgres/wowhua_api
ENV hnwowhua_db_admin_db postgresql://zch@wowhua_postgres/wowhua_admin
ENV hnwowhua_admin_MONGODB_SETTINGS__host wowhua_mongo

ENV  PIP_PYPI_URL http://myusername:mypasswd@pypi.lxdb.jiake.org/simple/
RUN  virtualenv /testenv && . /testenv/bin/activate && make config

EXPOSE 5000
CMD ["/testenv/bin/python", "scripts/run_wowhua_admin.py"]

