from dotenv import dotenv_values


class ConfigUtils:
    def __init__(self):
        config = dotenv_values("config/.env")
        self.mode = config.get('MODE')
        self.kafka_broker_url = config.get('KAFKA_BROKER_URL')
        self.kafka_group_id = config.get('KAFKA_GROUP_ID_FOR_WORKDER')
        self.video_events_ingestion_topic_name = config.get('VIDEO_EVENTS_INGESTION_TOPIC_NAME')
        self.video_events_ingestion_topic_partitions = int(config.get('VIDEO_EVENTS_INGESTION_TOPIC_PARTITIONS'))
        self.video_events_repartitioned_topic_name = config.get('VIDEO_EVENTS_REPARTITIONED_TOPIC_NAME')
        self.video_events_repartitioned_topic_partitions = int(config.get('VIDEO_EVENTS_REPARTITIONED_TOPIC_PARTITIONS'))
        self.likes_one_min_aggregation_topic_name = config.get('LIKES_1_MIN_AGGREGATION_TOPIC_NAME')
        self.likes_one_min_aggregation_topic_partitions = int(config.get('LIKES_1_MIN_AGGREGATION_TOPIC_PARTITIONS'))
        self.likes_five_min_aggregation_topic_name = config.get('LIKES_5_MIN_AGGREGATION_TOPIC_NAME')
        self.likes_five_min_aggregation_topic_partitions = int(config.get('LIKES_5_MIN_AGGREGATION_TOPIC_PARTITIONS'))
        self.likes_ten_min_aggregation_topic_name = config.get('LIKES_10_MIN_AGGREGATION_TOPIC_NAME')
        self.likes_ten_min_aggregation_topic_partitions = int(config.get('LIKES_10_MIN_AGGREGATION_TOPIC_PARTITIONS'))
        self.log_level = config.get('LOG_LEVEL')
        self.aggregation_table_name_1_min = config.get('AGGREGATION_TABLE_NAME_1_MIN')
        self.aggregation_table_name_5_min = config.get('AGGREGATION_TABLE_NAME_5_MIN')
        self.aggregation_table_name_10_min = config.get('AGGREGATION_TABLE_NAME_10_MIN')

    def in_dev_mode(self) -> bool:
        return self.mode == 'dev'

    @staticmethod
    def get_config() -> 'ConfigUtils':
        return ConfigUtils()
