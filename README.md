# Distributed Counter with Faust
This is a simplistic project that performs distributed stream processing (more specifically distributed counting of identifiers)
based on [faust](https://faust.readthedocs.io/en/latest/), [kafka](https://kafka.apache.org/) and [rocksdb](http://rocksdb.org/).
Kafka supports high throughput and low latency data ingestion (events that indicate a new count per identifier)
to our system. Then faust (backed-up by kafka) is used to partition the ingested data (events that represent a new count per identifier).
This way events are sharded using the identifier as a key, and each faust consumer always receives events for a given
identifier. Thus, each faust consumer is able to compute the aggregated counts of each identifier for a specific period
of time (1, 5, and 10 minutes in this project), and store it in its own in memory database.
Rocksdb is used by faust as an in memory database, while kafka is used as a [WAL](https://en.wikipedia.org/wiki/Write-ahead_logging)
that provides fault tolerance to it.
Finally, the cumulative count of identifiers is exposed in three kafka topics:
- **video_aggregations_1**, is a kafka topic with cumulative counts per identifier per minute
- **video_aggregations_5**, is a kafka topic with cumulative counts per identifier per five minutes
- **video_aggregations_10**, is a kafka topic with cumulative counts per identifier per ten minutes

> Note that the current project is not optimized for production. In order to have faust in a prod like enviroment one should
> ensure the following:
>   - faust is being executed in some kind of process control system like `supervisord`.
>   - at least 3 kafka brokers (as well as zookeper instances) are available.
>   - a policy for starting/stopping faust consumers is in place 
>   (should take into account [kafka rebalancing when a worker joins/leaves the cluster](https://faust.readthedocs.io/en/latest/userguide/workers.html#managing-a-cluster)).

## Technical notes
- Instead of robinhood's faust, the [faust-streaming](https://github.com/faust-streaming/faust) is used, which is a
    fork of it that it is actively maintained.
- In order to use `rocksdb` in our local machine the [yamitzky/docker-python-rocksdb](https://registry.hub.docker.com/r/yamitzky/docker-python-rocksdb)
    image is used. One can build (or alter) this image by using the [original Dockerfile](https://github.com/yamitzky/docker-python-rocksdb/blob/master/Dockerfile).
- Kafka advertised listeners are configured in order to expose kafka at `localhost:9094`.

# Local Setup

## Prerequisites
- docker >= 20.10.17
- docker-compose >= 1.26.2
- make file support
> If your system does not support make files you can manually execute the docker-compose commands in `makefile`.

## Initial configuration
```
git clone git@github.com:chrisbek/distributed-counter.git
docker network create -d bridge --attachable main-net --subnet 172.30.0.0/16 --gateway 172.30.0.255
cd /path/to/project
cp ./config/.env.dev ./config/.env -v
```

## Start Zookeeper & Kafka broker
```
make start-kafka
```

## Start Faust consumers
```
make start-faust
```

## Inspect containers' logs
You can always inspect the containers' logs using the following commands:
```
docker logs --follow zookeeper
docker logs --follow kafka-broker-1
docker logs --follow faust.worker.1
docker logs --follow faust.worker.2
```
It is expected that the leader of faust consumers will create "counting events" every 20 seconds, and that the cumulative
counting of these events will be available through the `video_aggregations_1`, `video_aggregations_5` and 
`video_aggregations_10` kafka topics, after the corresponding time has passed.

## Stop stack & Cleanup
- Stop running containers by:
```
make stop-faust
make stop-kafka
```

- Remove all data (from zookeeper, kafka, and faust consumers) by executing:
### Clean up data
```
cd /path/to/project
sudo rm -rf worker1/v1 worker2/v1 docker/zoo docker/kafka_files-1
```


## Event producer
Apart from having faust creating its own events (that is putting count identifiers into the ingestion topic (`video_clicks_ingestion`)) 
one can also ingest data to the system by using the `src.producer`. The producer is a simple serverless function
that exposes the endpoint `POST {stage}/videos/{video_id}/likes` in order to ingest data to the ingestion topic.
In order to start the producer one should execute the following commands:
```
yarn install
poetry shell
poetry install

cp serverless.dev.yml serverless.yml -v
serverless offline start --stage={stage}
```

> Note that [yarn](https://classic.yarnpkg.com/lang/en/docs/install/#debian-stable) 
> and [poetry](https://python-poetry.org/docs/#installation), and python >= 3.6 are required in order to start the consumer.

# Consuming the cumulative data
One can use the [kafka_consumer_websockets](https://github.com/chrisbek/kafka_consumer_websockets) in order to start
a SocketIO server in order to consume cumulative count of identifiers from the `video_aggregations_1`, `video_aggregations_5`,
and `video_aggregations_10` topics, and get these events through a websocket.

# Consuming and creating video likes through a UI
One can use the [distributed-counter-frontend](https://github.com/chrisbek/distributed-counter-frontend), a UI written
in react together with `kafka_consumer_websockets`, and this project, in order to:
- view a visual representation of videos based on video-identifiers
- configure the creation of likes per minute per video through the UI.
- generate the above number of likes per minute (per video) through the UI.
- inspect the live update of cumulative likes per video for 1', 5', and 10' through the UI.
