from rest_framework import serializers

class DistrictAirWeatherSerializer(serializers.Serializer):
    district_name = serializers.CharField()
    avg_temperature_2pm = serializers.FloatField()
    avg_pm2_5 = serializers.FloatField()
    lat = serializers.CharField()
    long = serializers.CharField()