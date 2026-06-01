import json
import time
import logging

from fastapi import APIRouter

from ifund_hq_project.models import ApiResponse, RankData, EtfRankItem
from ifund_hq_project.cache import get_from_local, put_to_local
from ifund_hq_project.redis_client import get_rank_data as redis_get_rank_data
from ifund_hq_project.config import RANK_DIMENSIONS, RANK_DIRECTIONS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/etf", tags=["ETF"])

EMPTY_RANK_DATA = RankData()


def _build_empty_response() -> dict:
    return _build_response(EMPTY_RANK_DATA)


def _build_response(rank_data: RankData) -> dict:
    resp = ApiResponse(
        code=0,
        message="success",
        data=rank_data,
        timestamp=int(time.time()),
    )
    return resp.model_dump()


def _parse_rank_json(raw: str) -> RankData | None:
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(obj, dict):
        return None
    try:
        return RankData(**obj)
    except Exception:
        return None


@router.get("/plate-stat/rank")
def get_plate_stat_etf_rank():
    # 1) Caffeine local cache
    cached = get_from_local()
    if cached is not None:
        parsed = _parse_rank_json(cached)
        if parsed is not None:
            return _build_response(parsed)
        # corrupt cache → invalidate and fall through
        from ifund_hq_project.cache import invalidate_local
        invalidate_local()

    # 2) Redis
    raw = redis_get_rank_data()

    if raw is None:
        # Redis unavailable or key missing → return empty structure
        return _build_empty_response()

    # 3) Populate Caffeine
    put_to_local(raw)

    # 4) Parse & respond
    parsed = _parse_rank_json(raw)
    if parsed is not None:
        return _build_response(parsed)

    # Redis data corrupt → empty fallback
    return _build_empty_response()
