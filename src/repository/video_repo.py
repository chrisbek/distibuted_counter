import uuid


def get_available_videos():
    return [
        {
            'unique_identifier': str(uuid.uuid4()),
            'title': 'Stream processing made simple'
        },
        {
            'unique_identifier': str(uuid.uuid4()),
            'title': 'Faust rocks'
        },
        {
            'unique_identifier': str(uuid.uuid4()),
            'title': 'How to create distributed counter'
        },
    ]
