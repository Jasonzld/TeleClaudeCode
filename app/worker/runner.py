"""RQ Worker entry point."""

from __future__ import annotations

import logging

from redis import Redis
from rq import Worker

from app.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def main() -> None:
    conn = Redis.from_url(settings.redis_url)
    worker = Worker([settings.queue_name], connection=conn)
    worker.work()


if __name__ == "__main__":
    main()
