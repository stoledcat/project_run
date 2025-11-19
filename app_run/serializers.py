from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Challenge, CollectibleItem, Position, Run


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

    def validate_run(self, value):
        if value.status != "in_progress":
            raise serializers.ValidationError("Забег не запущен или остановлен")
        return value

    def validate_latitude(self, value):
        if not (-90.0 <= value <= 90.0):
            raise serializers.ValidationError("Недопустимая широта")
        return value

    def validate_longitude(self, value):
        if not (-180.0 <= value <= 180.0):
            raise serializers.ValidationError("Недопустимая долгота")
        return value


class CollectibleItemSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)

    class Meta:
        model = CollectibleItem
        fields = ["uid", "latitude", "longitude", "url"]

    def validate_uid(self, uid):
        if not isinstance(uid, str) or len(uid) != 8:
            raise serializers.ValidationError("Недопустимый UID")
        return uid

    def validate_url(self, url):
        url_field = serializers.URLField()
        try:
            url = url_field.run_validation(url)
        except serializers.ValidationError:
            raise serializers.ValidationError("Недопустимый URL")
        return url
