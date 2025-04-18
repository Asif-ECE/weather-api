import datetime
import logging
import pandas as pd
import ast
import openmeteo_requests
import requests_cache
from retry_requests import retry
from rest_framework.exceptions import APIException


logger = logging.getLogger(__name__)

# Setting up Open-Meteo client with retry + caching
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo_client = openmeteo_requests.Client(session=retry_session)


# Validating district list and it's attributes
def _validate_districts(districts):
    if not isinstance(districts, list) or not all(isinstance(d, dict) for d in districts):
        raise ValueError("Districts must be a list of dictionaries.")
    for d in districts:
        if not all(k in d for k in ("name", "lat", "long")):
            raise ValueError("Each district must contain 'name', 'lat', and 'long'.")
        

def _fetch_hourly_data(url, districts, hourly_param, forecast_days=None):
    _validate_districts(districts)

    params = {
        "latitude": [d["lat"] for d in districts],
        "longitude": [d["long"] for d in districts],
        "hourly": hourly_param,
        "timezone": "Asia/Dhaka"
    }

    if forecast_days:
        params["forecast_days"] = forecast_days

    try:
        return openmeteo_client.weather_api(url, params=params)
    except Exception as e:
        logger.error(f"Error fetching {hourly_param} data: {str(e)}", exc_info=True)
        try:
            raise APIException(detail=ast.literal_eval(str(e)))
        except Exception:
            raise APIException(detail={"error": True, "reason": str(e)})
        

def _process_hourly_response(response, districts, param_key):
    data_list = []

    for i, res in enumerate(response):
        district = districts[i]
        hourly = res.Hourly()
        values = hourly.Variables(0).ValuesAsNumpy()
        times = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )

        df = pd.DataFrame({
            "date": times,
            param_key: values,
            "district_name": district["name"],
            "lat": district["lat"],
            "long": district["long"]
        })

        df_2pm = df[df["date"].dt.time == datetime.time(14, 0)]
        data_list.append(df_2pm)

    return pd.concat(data_list, ignore_index=True)


def get_batch_weather_info(districts):
    weather_url = "https://api.open-meteo.com/v1/forecast"
    response = _fetch_hourly_data(weather_url, districts, hourly_param="temperature_2m")
    return _process_hourly_response(response, districts, param_key="temperature_2m")


def get_batch_air_info(districts):
    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    response = _fetch_hourly_data(air_url, districts, hourly_param="pm2_5", forecast_days=7)
    return _process_hourly_response(response, districts, param_key="pm2_5")


def get_top_districts_to_visit(districts, result_range=10):
    weather_df = get_batch_weather_info(districts)
    air_df = get_batch_air_info(districts)

    combined_df = pd.merge(
        weather_df,
        air_df,
        on=['district_name', 'date'],
        suffixes=('_weather', '_air')
    )

    avg_df = combined_df.groupby("district_name").agg({
        "temperature_2m": "mean",
        "pm2_5": "mean",
        "lat_weather": "first",
        "long_weather": "first"
    }).rename(columns={
        "temperature_2m": "avg_temperature_2pm",
        "pm2_5": "avg_pm2_5",
        "lat_weather": "lat",
        "long_weather": "long"
    }).reset_index()

    top_districts = avg_df.sort_values(
        by=["avg_temperature_2pm", "avg_pm2_5"],
        ascending=[True, True]
    ).head(result_range)

    return top_districts


def compare_weather(source, destination, date):
    for location in [source, destination]:
        if not all(k in location for k in ("lat", "long")):
            raise ValueError("Both source and destination must have 'lat' and 'long' keys.")
        
    weather_url = "https://api.open-meteo.com/v1/forecast"
    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    common_params = {
        "timezone": "Asia/Dhaka",
        "start_date": date,
        "end_date": date
    }

    weather_params = {
        **common_params,
        "latitude": [source['lat'], destination['lat']],
        "longitude": [source['long'], destination['long']],
        "hourly": "temperature_2m",
    }

    air_params = {
        **common_params,
        "latitude": [source['lat'], destination['lat']],
        "longitude": [source['long'], destination['long']],
        "hourly": "pm2_5",
    }

    try:
        weather_responses = openmeteo_client.weather_api(weather_url, params=weather_params)
        air_responses = openmeteo_client.weather_api(air_url, params=air_params)
    except Exception as e:
        logger.error(f"Failed to fetch weather or air data: {str(e)}", exc_info=True)
        try:
            raise APIException(detail=ast.literal_eval(str(e)))
        except Exception:
            raise APIException(detail={"error": True, "reason": str(e)})

    result = {
        "temp_diff": float(weather_responses[1].Hourly().Variables(0).ValuesAsNumpy()[13]) -
                      float(weather_responses[0].Hourly().Variables(0).ValuesAsNumpy()[13]),
        "air_con_diff": float(air_responses[1].Hourly().Variables(0).ValuesAsNumpy()[13]) -
                        float(air_responses[0].Hourly().Variables(0).ValuesAsNumpy()[13]),
    }

    return result