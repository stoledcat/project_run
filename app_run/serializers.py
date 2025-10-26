from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Challenge, Position, Run


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "date_joined",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
        ]

    def get_type(self, obj):
        if obj.is_staff:
            return "coach"
        else:
            return "athlete"


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ["id", "full_name", "athlete"]


class AthleteDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "last_name", "first_name"]

    def get_type(self, obj):
        return obj.is_staff


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteDataSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    run = serializers.PrimaryKeyRelatedField(queryset=Run.objects.all())

    latitude = serializers.DecimalField(max_digits=7, decimal_places=4)
    longitude = serializers.DecimalField(max_digits=8, decimal_places=4)

    class Meta:
        model = Position
        fields = ["id", "run", "latitude", "longitude"]

    def validate(self, data):
        run = data.get("run")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if run.status != "in_progress":
            raise serializers.ValidationError("Забег не запущен или остановлен")

        if latitude and longitude:
            if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
                raise serializers.ValidationError("Указаны некорректные координаты")

        return data
