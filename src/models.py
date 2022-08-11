import faust
from abc import ABC


class VideoClick(faust.Record, ABC):
    identifier: str

    @staticmethod
    def from_raw_data(raw_data: bytes) -> 'VideoClick':
        return VideoClick(raw_data.decode("utf-8"))


class VideoAggregation(faust.Record, ABC):
    type: str
    video_uid: str
    count: int
