"""
URL configuration for the data_pipeline app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sensor-readings', views.SensorReadingViewSet, basename='sensor-reading')
router.register(r'grid-data', views.GridDataViewSet, basename='grid-data')
router.register(r'preferences', views.UserPreferencesViewSet, basename='preference')
router.register(r'ai-decisions', views.AIDecisionViewSet, basename='ai-decision')
router.register(r'energy-sources', views.EnergySourceViewSet, basename='energy-source')
router.register(r'loads', views.LoadViewSet, basename='load')
router.register(r'switch-events', views.SourceSwitchEventViewSet, basename='switch-event')
router.register(r'optimization', views.EnergyOptimizationViewSet, basename='optimization')

app_name = 'data_pipeline'

urlpatterns = [
    path('', include(router.urls)),
]
