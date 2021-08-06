from os import getenv

from redis import from_url
from rq import Connection, Worker

with Connection(from_url(getenv("REDIS_URL"))):
    Worker("queue").work()
