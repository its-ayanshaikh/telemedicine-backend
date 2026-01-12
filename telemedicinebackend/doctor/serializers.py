from rest_framework import serializers
from .models import *


class IndividualDoctorScheduleSerializer(serializers.ModelSerializer):

    start_time_display = serializers.SerializerMethodField()
    end_time_display = serializers.SerializerMethodField()

    class Meta:
        model = IndividualDoctorSchedule
        fields = (
            "id",
            "date",
            "day",
            "start_time",
            "end_time",
            "start_time_display",  # ✅ 12-hour
            "end_time_display",    # ✅ 12-hour
            "is_off",
            "reason",
        )

    def get_start_time_display(self, obj):
        if obj.start_time:
            return obj.start_time.strftime("%I:%M %p")
        return None

    def get_end_time_display(self, obj):
        if obj.end_time:
            return obj.end_time.strftime("%I:%M %p")
        return None




