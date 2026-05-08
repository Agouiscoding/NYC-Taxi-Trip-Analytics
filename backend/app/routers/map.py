from __future__ import annotations

from fastapi import APIRouter, Query

from backend.app import db
from backend.app.utils import clamp_limit, response


router = APIRouter(prefix="/map", tags=["map"])


def scoped_query(
    *,
    year: int | None = None,
    month: int | None = None,
    year_month: str | None = None,
    hour: int | None = None,
) -> dict:
    query: dict = {}
    if year is not None:
        query["year"] = year
    if month is not None:
        query["month"] = month
    if year_month:
        query["year_month"] = year_month
    if hour is not None:
        query["hour"] = hour
    return query


def borough_touch_query(query: dict, borough: str | None) -> dict:
    if not borough:
        return query
    return {
        **query,
        "$or": [
            {"pickup_borough": borough},
            {"dropoff_borough": borough},
        ],
    }


@router.get("/od-flow-hour")
def get_od_flow_hour(
    hour: int | None = Query(default=None, ge=0, le=23),
    borough: str | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=5000),
) -> dict:
    limit = clamp_limit(limit, default=500, maximum=5000)
    base_query = scoped_query(hour=hour)

    if borough:
        data = db.find_many(
            "map_od_flow_hour_by_borough",
            {**base_query, "scope_borough": borough},
            sort=[db.sort_asc("hour"), db.sort_asc("route_rank_in_borough_hour")],
            limit=limit,
        )
        if not data:
            data = db.find_many(
                "map_od_flow_hour",
                borough_touch_query(base_query, borough),
                sort=[db.sort_asc("hour"), db.sort_asc("route_rank_in_hour")],
                limit=limit,
            )
    else:
        data = db.find_many(
            "map_od_flow_hour",
            base_query,
            sort=[db.sort_asc("hour"), db.sort_asc("route_rank_in_hour")],
            limit=limit,
        )
    return response(data, hour=hour, borough=borough, limit=limit)


@router.get("/od-flow-year-month")
def get_od_flow_year_month(
    year: int | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=12),
    year_month: str | None = Query(default=None),
    borough: str | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=5000),
) -> dict:
    limit = clamp_limit(limit, default=500, maximum=5000)
    base_query = scoped_query(
        year=year,
        month=month,
        year_month=year_month,
    )

    if borough:
        data = db.find_many(
            "map_od_flow_year_month_by_borough",
            {**base_query, "scope_borough": borough},
            sort=[db.sort_asc("year"), db.sort_asc("month"), db.sort_asc("route_rank_in_borough_year_month")],
            limit=limit,
        )
        if not data:
            data = db.find_many(
                "map_od_flow_year_month",
                borough_touch_query(base_query, borough),
                sort=[db.sort_asc("year"), db.sort_asc("month"), db.sort_asc("route_rank_in_year_month")],
                limit=limit,
            )
    else:
        data = db.find_many(
            "map_od_flow_year_month",
            base_query,
            sort=[db.sort_asc("year"), db.sort_asc("month"), db.sort_asc("route_rank_in_year_month")],
            limit=limit,
        )
    return response(data, year=year, month=month, year_month=year_month, borough=borough, limit=limit)
