from django.contrib import admin
from .models import (
    HospitalDoctor,
    HospitalDoctorSchedule,
    HospitalDoctorOff,
    HospitalDoctorFee
)


class HospitalDoctorScheduleInline(admin.TabularInline):
    model = HospitalDoctorSchedule
    extra = 1


@admin.register(HospitalDoctor)
class HospitalDoctorAdmin(admin.ModelAdmin):
    list_display = ("hospital", "doctor", "created_at")
    search_fields = ("hospital__username", "doctor__username")
    list_filter = ("created_at",)
    inlines = [HospitalDoctorScheduleInline]


@admin.register(HospitalDoctorOff)
class HospitalDoctorOffAdmin(admin.ModelAdmin):
    list_display = ("hospital_doctor", "date", "status")
    list_filter = ("status", "date")


@admin.register(HospitalDoctorFee)
class HospitalDoctorFeeAdmin(admin.ModelAdmin):
    list_display = ("hospital_doctor", "amount")