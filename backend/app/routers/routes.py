from __future__ import annotations

from fastapi import APIRouter, Query

from backend.app import db
from backend.app.utils import clamp_limit, response


router = APIRouter(prefix="/routes", tags=["routes"])


def scoped_route_rows(
    *,
    borough: str | None,
    overall_collection: str,
    scoped_collection: str,
    overall_sort: list[tuple[str, int]],
    limit: int,
) -> list[dict]:
    if borough:
        data = db.find_many(
            scoped_collection,
            {"scope_borough": borough},
            sort=[db.sort_asc("route_rank_in_borough"), db.sort_desc("trip_count")],
            limit=limit,
        )
        if data:
            return data

        return db.find_many(
            overall_collection,
            {
                "$or": [
                    {"pickup_borough": borough},
                    {"dropoff_borough": borough},
                ],
            },
            sort=overall_sort,
            limit=limit,
        )

    return db.find_many(
        overall_collection,
        sort=overall_sort,
        limit=limit,
    )


@router.get("/top")
def get_top_routes(
    borough: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=500),
) -> dict:
    limit = clamp_limit(limit, default=25, maximum=500)
    data = scoped_route_rows(
        borough=borough,
        overall_collection="routes_top_routes",
        scoped_collection="routes_top_routes_by_borough",
        overall_sort=[db.sort_asc("route_rank")],
        limit=limit,
    )
    return response(data, borough=borough, limit=limit)


@router.get("/airport")
def get_airport_routes(
    borough: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=500),
) -> dict:
    limit = clamp_limit(limit, default=25, maximum=500)
    data = scoped_route_rows(
        borough=borough,
        overall_collection="routes_top_airport_routes",
        scoped_collection="routes_top_airport_routes_by_borough",
        overall_sort=[db.sort_asc("route_rank"), db.sort_desc("trip_count")],
        limit=limit,
    )
    return response(data, borough=borough, limit=limit)


@router.get("/inter-borough")
def get_inter_borough_routes(
    borough: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=500),
) -> dict:
    limit = clamp_limit(limit, default=25, maximum=500)
    data = scoped_route_rows(
        borough=borough,
        overall_collection="routes_top_inter_borough_routes",
        scoped_collection="routes_top_inter_borough_routes_by_borough",
        overall_sort=[db.sort_asc("route_rank"), db.sort_desc("trip_count")],
        limit=limit,
    )
    return response(data, borough=borough, limit=limit)


@router.get("/borough-matrix")
def get_route_borough_matrix() -> dict:
    data = db.find_many(
        "routes_borough_matrix",
        sort=[db.sort_desc("total_trips")],
    )
    return response(data)


@router.get("/pickup-dropoff-borough-matrix")
def get_pickup_dropoff_borough_matrix() -> dict:
    data = db.find_many(
        "routes_pickup_dropoff_borough_matrix",
        sort=[db.sort_desc("trip_count")],
    )
    return response(data)


@router.get("/airport-summary")
def get_airport_trip_summary(year: int | None = Query(default=None)) -> dict:
    query = {"year": year} if year else {}
    data = db.find_many(
        "routes_airport_trip_summary",
        query,
        sort=[db.sort_asc("year"), db.sort_asc("airport_trip_type")],
    )
    return response(data, year=year)


@router.get("/concentration")
def get_route_concentration(limit: int = Query(default=500, ge=1, le=5000)) -> dict:
    data = db.find_many(
        "route_concentration",
        sort=[db.sort_asc("route_order")],
        limit=limit,
    )
    return response(data, limit=limit)
