from fastapi import APIRouter

from app.apis.globalAPI import get_global_stats, GlobalStats

router = APIRouter()


@router.get("", response_model=GlobalStats)
def get_global_statistics():
    return get_global_stats()
