from django.contrib import admin
from .models import (

    IndividualDoctorSchedule,
)

@admin.register(IndividualDoctorSchedule)
class IndividualDoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ("doctor","date", "day", "start_time", "end_time", "is_off", "reason")
    list_filter = ("day",)


