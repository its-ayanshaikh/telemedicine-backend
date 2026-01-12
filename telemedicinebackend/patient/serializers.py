from rest_framework import serializers
from .models import *
from Authentication.models import User

class AppointmentSerializer(serializers.ModelSerializer):

    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "doctor_name",
            "patient",
            "patient_name",
            "appointment_date",
            "start_time",
            "end_time",
            "status",
            "payment_status",
            "amount",
            "doctor_link",
            "patient_link",
            "razorpay_order_id",
            "razorpay_payment_id",
            "transcription_file",
            "created_at",
        ]

    def get_doctor_name(self, obj):
        if obj.doctor:
            return f"{obj.doctor.first_name} {obj.doctor.last_name}".strip()
        return None

    def get_patient_name(self, obj):
        if obj.patient:
            return f"{obj.patient.first_name} {obj.patient.last_name}".strip()
        return None


class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = [
            "id",
            "medicine_name",
            "dose",
            "frequency",
            "timing",
            "duration"
        ]
        
class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = PrescriptionMedicineSerializer(many=True, read_only=True)
    appointment_id = serializers.IntegerField(source="appointment.id", read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id",
            "appointment_id",
            "diagnosis",
            "additional_notes",
            "digital_signature",
            "medicines",
            "created_at"
        ]
        
class DoctorPatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "age",
            "gender",
            "mobile_number",
            "city",
            "state"
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()