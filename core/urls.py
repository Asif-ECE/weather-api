from django.urls import path
from .views import TopDistricts, TravelRecommendation

app_name = 'core'

urlpatterns = [
    path('best-cities-to-visit/', TopDistricts.as_view(), name='best-cities-to-visit'),
    path('travel-recommendation/', TravelRecommendation.as_view(), name='travel-recommendation'),
]