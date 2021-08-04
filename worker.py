from os import getenv

from rq import Connection, Worker

from redis import from_url

with Connection(from_url(getenv("REDIS_URL"))):
    Worker("default").work()
