from django.urls import path
from .views import (RocketControlView, 
                   TelemetryDataView, 
                   LaunchLogView,
                   UserCreateView)

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('control/', RocketControlView.as_view(), name='rocket-control'),
    path('telemetry/', TelemetryDataView.as_view(), name='telemetry-data'),
    path('logs/', LaunchLogView.as_view(), name='launch-logs'),
]