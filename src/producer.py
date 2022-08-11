from src.repository import video_repo
from src.utils import queue_utils
import json
from kafka.producer import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9094', value_serializer=queue_utils.serializer)


def count_video_like(event, context):
    video_identifier = event['pathParameters']['video_id']
    producer.send(topic='video_clicks_ingestion', value=video_identifier)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            'new video': video_identifier
        })
    }


def get_available_videos(event, context):
    available_videos = video_repo.get_available_videos()
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(available_videos)
    }
