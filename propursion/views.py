from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth.models import User
from .models import RocketStatus, TelemetryData, LaunchLog
from .serializers import (RocketStatusSerializer, 
                         TelemetryDataSerializer, 
                         LaunchLogSerializer,
                         UserSerializer)
from django.shortcuts import get_object_or_404
import time

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class RocketControlView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        rocket, created = RocketStatus.objects.get_or_create(user=request.user)
        serializer = RocketStatusSerializer(rocket)
        return Response(serializer.data)
    
    def post(self, request):
        action = request.data.get('action')
        rocket, created = RocketStatus.objects.get_or_create(user=request.user)
        
        if action == 'power_on':
            rocket.power_status = 'ON'
            rocket.launch_initiated = None
            rocket.save()
            LaunchLog.objects.create(
                rocket=rocket,
                action='POWER_ON',
                details='User powered on the rocket systems'
            )
            return Response({'status': 'Power ON'})
        
        elif action == 'power_off':
            rocket.power_status = 'OFF'
            rocket.launch_initiated = None
            rocket.save()
            LaunchLog.objects.create(
                rocket=rocket,
                action='POWER_OFF',
                details='User powered off the rocket systems'
            )
            return Response({'status': 'Power OFF'})
        
        elif action == 'launch':
            if rocket.power_status == 'ON':
                rocket.launch_initiated = timezone.now()
                rocket.save()
                LaunchLog.objects.create(
                    rocket=rocket,
                    action='LAUNCH_INITIATED',
                    details='User initiated launch sequence'
                )
                
                # Simulate the 10-second abort window
                def check_abort():
                    time.sleep(10)
                    rocket.refresh_from_db()
                    if rocket.power_status == 'ON' and rocket.launch_initiated and (timezone.now() - rocket.launch_initiated).total_seconds() >= 10:
                        rocket.power_status = 'LAUNCHED'
                        rocket.save()
                        LaunchLog.objects.create(
                            rocket=rocket,
                            action='LAUNCH_SUCCESS',
                            details='Rocket successfully launched after abort window'
                        )
                
                import threading
                threading.Thread(target=check_abort).start()
                
                return Response({
                    'status': 'Launch initiated',
                    'abort_window': 'You have 10 seconds to abort'
                })
            return Response({'error': 'Rocket must be powered on to launch'}, status=400)
        
        elif action == 'abort':
            if rocket.can_abort():
                rocket.power_status = 'ABORTED'
                rocket.save()
                LaunchLog.objects.create(
                    rocket=rocket,
                    action='LAUNCH_ABORTED',
                    details='User aborted launch within the 10-second window'
                )
                return Response({'status': 'Launch aborted'})
            return Response({'error': 'Cannot abort outside the 10-second window'}, status=400)
        
        return Response({'error': 'Invalid action'}, status=400)

class TelemetryDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        rocket = get_object_or_404(RocketStatus, user=request.user)
        if rocket.power_status != 'LAUNCHED':
            return Response({'error': 'Rocket must be launched to send telemetry'}, status=400)
        
        serializer = TelemetryDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(rocket=rocket)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request):
        rocket = get_object_or_404(RocketStatus, user=request.user)
        telemetry = TelemetryData.objects.filter(rocket=rocket).order_by('-timestamp')
        serializer = TelemetryDataSerializer(telemetry, many=True)
        return Response(serializer.data)

class LaunchLogView(generics.ListAPIView):
    serializer_class = LaunchLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        rocket = get_object_or_404(RocketStatus, user=self.request.user)
        return LaunchLog.objects.filter(rocket=rocket).order_by('-timestamp')