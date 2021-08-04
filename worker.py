import os

import redis
from rq import Connection, Queue, Worker

with Connection(redis.from_url(os.getenv("REDISTOGO_URL"))):
    Worker("default").work()
