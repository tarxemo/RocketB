from rest_framework import serializers
from .models import RocketStatus, TelemetryData, LaunchLog
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RocketStatusSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    can_abort = serializers.SerializerMethodField()
    
    class Meta:
        model = RocketStatus
        fields = ['id', 'user', 'power_status', 'launch_initiated', 'last_updated', 'can_abort']
    
    def get_can_abort(self, obj):
        return obj.can_abort()

class TelemetryDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryData
        fields = '__all__'

class LaunchLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaunchLog
        fields = '__all__'