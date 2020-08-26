from fastapi import APIRouter

from app.apis.globalAPI import get_global_stats, GlobalStats

router = APIRouter()


@router.get("", response_model=GlobalStats)
def api_get_global_stats():
    return get_global_stats()
