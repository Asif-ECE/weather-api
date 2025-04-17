from datetime import datetime, date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from utils.openmateo_client import get_top_districts_to_visit, compare_weather
from utils.district_data_loader import get_districts
from utils.message_generator import generate_weather_message
from .serializers import DistrictAirWeatherSerializer


class TopDistricts(APIView):
    def get(self, request):
        try:
            districts = get_districts()

        except Exception as e:
            return Response({
                "success": False,
                "message": "Unable to load district data.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        top_10_districts = get_top_districts_to_visit(districts, result_range=10)
        serializer = DistrictAirWeatherSerializer(top_10_districts.to_dict(orient="records"), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TravelRecommendation(APIView):
    def get(self, request):
        destination = request.query_params.get('destination', None)
        lat = request.query_params.get('lat', None)
        long = request.query_params.get('long', None)
        travel_date_str = request.query_params.get('date', None)

        if not all([destination, lat, long, travel_date_str]):
            return Response({
                "error": True,
                "message": "Missing required query parameters: destination, lat, long, and date."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            current_lat = float(lat)
            current_long = float(long)
            travel_date = datetime.strptime(travel_date_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValidationError(f"Invalid parameter format: {e}")
        
        if travel_date < date.today():
            return Response({
                "error": True,
                "message": "Travel date cannot be in the past. Choose a date between today and 15 days from now."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            districts = get_districts()
        except Exception as e:
            return Response({
                "success": False,
                "message": "Unable to load district data.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        district_info = next((d for d in districts if d["name"].lower() == destination.lower()), None)
        if not district_info:
            return Response({
                "success": False,
                "message": f"Destination '{destination}' not found in district list."
            }, status=status.HTTP_400_BAD_REQUEST)

        result = compare_weather(
            source={"lat": current_lat, "long": current_long},
            destination={"lat": district_info.get("lat"), "long": district_info.get("long")},
            date=travel_date.strftime("%Y-%m-%d")
        )

        recommendation = "Recommended" if result["temp_diff"] < 0 and result["air_con_diff"] < 0 else "Not Recommended"

        return Response({
            "recommendation": recommendation,
            "message" : generate_weather_message(result)
        }, status=status.HTTP_200_OK)