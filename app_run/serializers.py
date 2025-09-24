from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Run


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "date_joined", "username", "last_name", "first_name", "type"]

    def get_type(self, obj):
        if obj.is_staff:
            return "coach"
        else:
            return "athlete"


class AthleteDataSerializer(serializers.ModelSerializer):
    # type = serializers.SerializerMethodField()

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
