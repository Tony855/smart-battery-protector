"""Runtime factories for MariaDB and Redis. No network connection at import time."""
from __future__ import annotations

import os
from functools import lru_cache

import pymysql
import redis


def database_connection():
    required = ("SBP_DB_HOST", "SBP_DB_USER", "SBP_DB_PASSWORD", "SBP_DB_NAME")
    if any(not os.getenv(key) for key in required):
        raise RuntimeError("database_configuration_missing")
    return pymysql.connect(
        host=os.environ["SBP_DB_HOST"],
        port=int(os.getenv("SBP_DB_PORT", "3306")),
        user=os.environ["SBP_DB_USER"],
        password=os.environ["SBP_DB_PASSWORD"],
        database=os.environ["SBP_DB_NAME"],
        connect_timeout=3,
        read_timeout=3,
        write_timeout=3,
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )


@lru_cache(maxsize=1)
def redis_client():
    url = os.getenv("SBP_REDIS_URL")
    if not url:
        raise RuntimeError("redis_configuration_missing")
    return redis.Redis.from_url(
        url, socket_connect_timeout=3, socket_timeout=3,
        health_check_interval=30, decode_responses=True,
    )
