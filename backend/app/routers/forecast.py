from __future__ import annotations

from fastapi import APIRouter, Query

from backend.app import db
from backend.app.utils import clamp_limit, response


router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/story")
def get_forecast_story(zone_limit: int = Query(default=300, ge=1, le=500)) -> dict:
    zone_limit = clamp_limit(zone_limit, default=300, maximum=500)

    story = {
        "model_evaluation_metrics": db.find_many(
            "forecast_model_evaluation_metrics",
            sort=[db.sort_asc("RMSE")],
        ),
        "monthly_actual_predicted": db.find_many(
            "forecast_monthly_actual_predicted",
            sort=[db.sort_asc("year_month")],
        ),
        "daily_actual_predicted": db.find_many(
            "forecast_daily_actual_predicted",
            sort=[db.sort_asc("pickup_date")],
        ),
        "error_by_hour": db.find_many(
            "forecast_error_by_hour",
            sort=[db.sort_asc("hour")],
        ),
        "error_by_borough": db.find_many(
            "forecast_error_by_borough",
            sort=[db.sort_desc("aggregate_absolute_error")],
        ),
        "zone_accuracy": db.find_many(
            "forecast_zone_accuracy",
            sort=[db.sort_desc("aggregate_absolute_error")],
            limit=zone_limit,
        ),
    }

    return response(story, evaluation_year=2024, zone_limit=zone_limit)
