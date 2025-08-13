from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class RocketStatus(models.Model):
    POWER_CHOICES = [
        ('OFF', 'Power Off'),
        ('ON', 'Power On'),
        ('LAUNCHED', 'Launched'),
        ('ABORTED', 'Aborted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    power_status = models.CharField(max_length=10, choices=POWER_CHOICES, default='OFF')
    launch_initiated = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def can_abort(self):
        if self.power_status == 'ON' and self.launch_initiated:
            return (timezone.now() - self.launch_initiated).total_seconds() <= 10
        return False
    
    def __str__(self):
        return f"{self.user.username}'s Rocket: {self.power_status}"

class TelemetryData(models.Model):
    rocket = models.ForeignKey(RocketStatus, on_delete=models.CASCADE, related_name='telemetry_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    mass = models.FloatField(help_text="Mass in kg")
    roll = models.FloatField(help_text="Roll angle in degrees")
    pitch = models.FloatField(help_text="Pitch angle in degrees")
    yaw = models.FloatField(help_text="Yaw angle in degrees")
    temperature = models.FloatField(help_text="Temperature in °C")
    pressure = models.FloatField(help_text="Pressure in kPa")
    acceleration = models.FloatField(help_text="Acceleration in m/s²")
    speed = models.FloatField(help_text="Speed in m/s")
    altitude = models.FloatField(help_text="Altitude in meters")
    gps_position = models.CharField(max_length=50, help_text="GPS coordinates (lat,long)")
    x_sensor_safe_status = models.BooleanField(help_text="Sensor safety status")
    
    def __str__(self):
        return f"Telemetry at {self.timestamp}"

class LaunchLog(models.Model):
    rocket = models.ForeignKey(RocketStatus, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)
    details = models.TextField()
    
    def __str__(self):
        return f"{self.action} at {self.timestamp}"