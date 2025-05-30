from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from utils.openmateo_client import get_top_districts_to_visit, compare_weather
from utils.district_data_loader import get_districts
from utils.message_generator import generate_weather_message
from .serializers import DistrictAirWeatherSerializer, TravelRecommendationQuerySerializer


@extend_schema(
    summary="Top Districts to Visit",   
    description="Returns a list of the top 10 districts in Bangladesh recommended for travel based on weather and air quality.",
    tags=["Travel"],
    responses={
        200: DistrictAirWeatherSerializer(many=True),
        500: OpenApiExample(
            name="Server Error",
            value={"success": False, "message": "Unable to load district data."}
        )
    },
)
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
        serializer = DistrictAirWeatherSerializer(top_10_districts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Travel Recommendation",
    description=(
        "Compares weather and air quality between the source and destination locations "
        "and recommends whether it's a good idea to travel on the given date."
    ),
    tags=["Travel"],
    parameters=[
        OpenApiParameter(name='destination', type=str, required=True, location=OpenApiParameter.QUERY, description='Destination district name'),
        OpenApiParameter(name='lat', type=float, required=True, location=OpenApiParameter.QUERY, description='Latitude of source location'),
        OpenApiParameter(name='long', type=float, required=True, location=OpenApiParameter.QUERY, description='Longitude of source location'),
        OpenApiParameter(name='date', type=str, required=True, location=OpenApiParameter.QUERY, description='Travel date (YYYY-MM-DD)')
    ],
    responses={
        200: OpenApiExample(
            name="Recommendation Success",
            value={
                "success": True,
                "recommendation": "Recommended",
                "message": "Weather is cooler and air quality is better in the destination."
            }
        ),
        400: OpenApiExample(
            name="Validation Error",
            value={"success": False, "message": "Destination 'foobar' not found in district list."}
        ),
        500: OpenApiExample(
            name="Server Error",
            value={"success": False, "message": "Unable to load district data."}
        )
    },
)
class TravelRecommendation(APIView):    
    def get(self, request):
        serializer = TravelRecommendationQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        destination = validated_data["destination"]
        lat = validated_data["lat"]
        long = validated_data["long"]
        travel_date_str = validated_data["date"]
        
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
            source={"lat": lat, "long": long},
            destination={"lat": district_info.get("lat"), "long": district_info.get("long")},
            date=travel_date_str.strftime("%Y-%m-%d")
        )

        recommendation = "Recommended" if result["temp_diff"] < 0 and result["air_con_diff"] < 0 else "Not Recommended"

        return Response({
            "success": True,
            "recommendation": recommendation,
            "message" : generate_weather_message(result)
        }, status=status.HTTP_200_OK)