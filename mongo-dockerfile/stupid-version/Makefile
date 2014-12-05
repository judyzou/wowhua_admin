.PHONY: clean-pyc clean-build docs

docker_build:
	docker build -t wowhua-mongo .

docker_tag:
	docker tag wowhua-mongo docker-registry.lxdb.jiake.org/wowhua_mongo

docker_push:
	docker push docker-registry.lxdb.jiake.org/wowhua_mongo

docker_clean:
	docker rm -v wowhua-mongo
	docker rmi docker-registry.lxdb.jiake.org/wowhua_mongo

# after push, we can use the release image for testing
docker_run:
	docker run -p 0.0.0.0:27017:27017 --name run-wowhua-mongo -d docker-registry.lxdb.jiake.org/wowhua_mongo

docker_debug:
	docker run -it --name run-wowhua-mong --rm wowhua-mongo

docker_test:
	docker run -it --link run-wowhua-mongo:wowhua_db_mongo --rm wowhua-mongo sh -c 'exec mongo "$$WOWHUA_DB_MONGO_PORT_27017_TCP_ADDR:$$WOWHUA_DB_MONGO_PORT_27017_TCP_PORT/test"'
	docker run -it --link run-wowhua-mongo:wowhua_db_mongo --rm wowhua-mongo sh -c 'env'
	nc -zv localhost 27017

docker_stop:
	docker stop run-wowhua-mongo

docker_rm:
	docker rm run-wowhua-mongo

docker_start:
	docker start run-wowhua-mongo

