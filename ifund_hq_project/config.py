import os

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_SOCKET_TIMEOUT = int(os.getenv("REDIS_SOCKET_TIMEOUT", "2"))
REDIS_SOCKET_CONNECT_TIMEOUT = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "2"))

RANK_DATA_KEY = "plateStatEtf:rank:data"

CAFFEINE_TTL_SECONDS = int(os.getenv("CAFFEINE_TTL_SECONDS", "30"))

RANK_DIMENSIONS = [
    "changeRatio",
    "speedRatio",
    "volumeRatio",
    "limitUpCount",
]

RANK_DIRECTIONS = ["Top9", "Bottom9"]
