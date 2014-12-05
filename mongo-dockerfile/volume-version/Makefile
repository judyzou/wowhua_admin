.PHONY: clean-pyc clean-build docs


docker_data:
	docker run -i -t --name mongo_data -v /tmp/mgdata:/data/ busybox /bin/sh

docker_run:
	docker run -p 127.0.0.1:27017:27017 --name run-wowhua-db-mongo -d --volumes-from mongo_data dockerfile/mongodb

docker_test:
	docker run -it --link run-wowhua-db-mongo:wowhua_db_mongo --rm dockerfile/mongodb sh -c 'exec mongo "$$WOWHUA_DB_MONGO_PORT_27017_TCP_ADDR:$$WOWHUA_DB_MONGO_PORT_27017_TCP_PORT/test"'
	docker run -it --link run-wowhua-db-mongo:wowhua_db_mongo --rm dockerfile/mongodb sh -c 'env'

docker_stop:
	docker stop run-wowhua-db-mongo

docker_rm:
	docker rm run-wowhua-db-mongo

docker_start:
	docker start run-wowhua-db-mongo
