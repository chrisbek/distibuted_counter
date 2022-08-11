from src.models import VideoClick, VideoAggregation
import faust
from datetime import timedelta
import random
from src.utils.config_utils import ConfigUtils
from src.utils.log_service import LogService

config = ConfigUtils.get_config()
logger = LogService.get_logger(config.log_level)

app = faust.App(
    config.kafka_group_id,
    broker=config.kafka_broker_url,
    store='rocksdb://',
    replication_factor=1
)
app.conf.table_cleanup_interval = 20.0

video_clicks_ingestion_topic = app.topic(
    config.video_events_ingestion_topic_name,
    value_serializer='raw',
    retention=900,  # Number of seconds to keep messages in the topic before they can be expired.
    partitions=config.video_events_ingestion_topic_partitions
)

video_clicks_grouped_by_identifier = app.topic(
    config.video_events_repartitioned_topic_name,
    value_serializer='raw',
    retention=900,
    partitions=config.video_events_repartitioned_topic_partitions
)

one_minute_aggregation_topic = app.topic(
    config.likes_one_min_aggregation_topic_name,
    value_type=VideoAggregation,
    retention=900,
    partitions=config.likes_one_min_aggregation_topic_partitions
)

five_minute_aggregation_topic = app.topic(
    config.likes_five_min_aggregation_topic_name,
    value_type=VideoAggregation,
    retention=900,
    partitions=config.likes_five_min_aggregation_topic_partitions
)

ten_minute_aggregation_topic = app.topic(
    config.likes_ten_min_aggregation_topic_name,
    value_type=VideoAggregation,
    retention=900,
    partitions=config.likes_ten_min_aggregation_topic_partitions
)


async def process_one_minute_window(metadata, value) -> None:
    key, window = metadata
    await one_minute_aggregation_topic.send(
        value=VideoAggregation(
            type='1min',
            video_uid=key,
            count=value
        ))


async def process_five_minute_window(metadata, value) -> None:
    key, window = metadata
    await five_minute_aggregation_topic.send(
        value=VideoAggregation(
            type='5min',
            video_uid=key,
            count=value
        ))


async def process_ten_minute_window(metadata, value) -> None:
    key, window = metadata
    await ten_minute_aggregation_topic.send(
        value=VideoAggregation(
            type='10min',
            video_uid=key,
            count=value
        ))


video_counts_1_min = (
    app.Table(
        config.aggregation_table_name_1_min,
        default=int,
        partitions=config.video_events_repartitioned_topic_partitions,
        on_window_close=process_one_minute_window)
    .tumbling(timedelta(minutes=1), expires=timedelta(minutes=1), key_index=True)
    .relative_to_stream())
app.tables.add(video_counts_1_min.key_index_table)

video_counts_5_min = (
    app.Table(
        config.aggregation_table_name_5_min,
        default=int,
        partitions=config.video_events_repartitioned_topic_partitions,
        on_window_close=process_five_minute_window)
    .tumbling(timedelta(minutes=5), expires=timedelta(minutes=5), key_index=True)
    .relative_to_stream())
app.tables.add(video_counts_5_min.key_index_table)

video_counts_10_min = (
    app.Table(
        config.aggregation_table_name_10_min,
        default=int,
        partitions=config.video_events_repartitioned_topic_partitions,
        on_window_close=process_ten_minute_window)
    .tumbling(timedelta(minutes=10), expires=timedelta(minutes=10), key_index=True)
    .relative_to_stream())
app.tables.add(video_counts_10_min.key_index_table)


def _get_key_from_raw_video_data(raw_data):
    return VideoClick.from_raw_data(raw_data).identifier


@app.agent(video_clicks_ingestion_topic)
async def process_video_identifiers(stream: faust.Stream):
    async for raw_data in stream.group_by(
            key=_get_key_from_raw_video_data,
            topic=video_clicks_grouped_by_identifier,
            name='dummy_suffix'):
        yield raw_data


@app.agent(video_clicks_grouped_by_identifier)
async def count_video_identifiers(stream: faust.Stream):
    async for raw_data in stream:
        video = VideoClick.from_raw_data(raw_data)
        video_counts_1_min[video.identifier] += 1
        logger.info(
            video_counts_1_min.as_ansitable(
                key='video_per_1_min',
                value='count',
                sort=True
            )
        )


@app.agent(video_clicks_grouped_by_identifier)
async def count_video_identifiers_5(stream: faust.Stream):
    async for raw_data in stream:
        video = VideoClick.from_raw_data(raw_data)
        video_counts_5_min[video.identifier] += 1
        logger.info(
            video_counts_5_min.as_ansitable(
                key='video_per_5_min',
                value='count',
                sort=True
            )
        )


@app.agent(video_clicks_grouped_by_identifier)
async def count_video_identifiers_10(stream: faust.Stream):
    async for raw_data in stream:
        video = VideoClick.from_raw_data(raw_data)
        video_counts_10_min[video.identifier] += 1
        logger.info(
            video_counts_10_min.as_ansitable(
                key='video_per_10_min',
                value='count',
                sort=True
            )
        )


@app.agent(one_minute_aggregation_topic)
async def report_aggregated_1_min_data(stream: faust.Stream):
    async for aggregation in stream:
        logger.info(f'Total 1\' likes for {aggregation.video_uid}: {aggregation.count}')


@app.agent(five_minute_aggregation_topic)
async def report_aggregated_5_min_data(stream: faust.Stream):
    async for aggregation in stream:
        logger.info(f'Total 5\' likes for {aggregation.video_uid}: {aggregation.count}')


@app.agent(ten_minute_aggregation_topic)
async def report_aggregated_10_min_data(stream: faust.Stream):
    async for aggregation in stream:
        logger.info(f'Total 10\' likes for {aggregation.video_uid}: {aggregation.count}')


@app.timer(20.0, on_leader=True)
async def generate_fake_events():
    if not config.in_dev_mode():
        return

    video_identifiers = ['93f98662-8907-4f43-bb4c-280501481046', '69e7266c-753e-4ed3-b7fc-9035133a293f']
    like_clicked_event = random.choice(video_identifiers)
    logger.info(f'Like for video: {like_clicked_event}')

    await video_clicks_ingestion_topic.send(
        value=like_clicked_event.encode("utf-8")
    )
