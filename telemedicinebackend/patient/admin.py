from django.contrib import admin
from .models import *


    
class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 1

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "created_at")
    search_fields = ("appointment__doctor__email", "appointment__patient__email")
    inlines = [PrescriptionMedicineInline]

class PrescriptionInline(admin.StackedInline):
    model = Prescription
    can_delete = False
    extra = 0

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "appointment_date",
        "start_time",
        "end_time",
        "doctor",
        "patient",
        "status",
        "payment_status",
        "amount",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "appointment_date",
        "doctor",
    )

    search_fields = (
        "doctor__mobile_number",
        "patient__mobile_number",
        "razorpay_order_id",
        "razorpay_payment_id",
    )

    readonly_fields = (
        "razorpay_order_id",
        "razorpay_payment_id",
        "created_at",
    )

    fieldsets = (
        ("Appointment Info", {
            "fields": (
                "doctor",
                "patient",
                "appointment_date",
                "start_time",
                "end_time",
                "doctor_link",
                "patient_link",
                "status",
                
            )
        }),
        ("Payment Info", {
            "fields": (
                "amount",
                "payment_status",
                "razorpay_order_id",
                "razorpay_payment_id",
            )
        }),
        ("Transcription", {
            "fields": ("transcription_file",)
        }),
        ("Meta", {
            "fields": ("created_at",)
        }),
    )

    ordering = ("-created_at",)

    inlines = [PrescriptionInline]