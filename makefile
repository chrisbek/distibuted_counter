start-kafka:
	docker-compose -f docker/docker-compose.kafka.yaml up -d

stop-kafka:
	docker-compose -f docker/docker-compose.kafka.yaml down

start-faust:
	docker-compose -f docker/docker-compose.yaml up -d

stop-faust:
	docker-compose -f docker/docker-compose.yaml down

.PHONY: start-kafka stop-kafka start-faust stop-faust