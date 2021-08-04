import os

import redis
from rq import Connection, Queue, Worker

with Connection(redis.from_url(os.getenv("REDIS_URL"))):
    Worker("default").work()
