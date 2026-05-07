from __future__ import annotations

from fastapi import APIRouter, Query

from backend.app import db
from backend.app.utils import response


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def get_overview() -> dict:
    overview = {
        "kpi": db.find_one("kpi_summary") or {},
        "yearly_summary": db.find_many(
            "temporal_yearly_summary",
            sort=[db.sort_asc("year")],
        ),
    }

    return response(overview)


@router.get("/business-story")
def get_business_story(year: int | None = Query(default=None)) -> dict:
    story = {
        "payment_type": db.find_many(
            "business_payment_type_by_year" if year else "business_payment_type_summary",
            {"year": year} if year else {},
            sort=[db.sort_desc("trip_count")],
        ),
    }

    return response(story, year=year)
