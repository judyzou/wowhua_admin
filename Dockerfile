FROM python:2.7.8

RUN apt-get update

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/

ENV PIP_PYPI_URL http://myusername:mypasswd@pypi.lxdb.jiake.org/simple/
RUN virtualenv /testenv && . /testenv/bin/activate && pip install -r requirements.txt

COPY . /app
RUN . /testenv/bin/activate && make config

EXPOSE 5000
CMD ["/testenv/bin/python", "scripts/manage.py", "runserver", "-h", "0.0.0.0", "-p", "5000"]

