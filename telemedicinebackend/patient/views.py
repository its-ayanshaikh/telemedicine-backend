from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import *
import razorpay
from django.conf import settings
from decimal import Decimal
from .serializers import *
from datetime import date
from django.db import transaction

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_razorpay_order(request):

    try:
        amount = request.data.get("amount")  # in rupees
        print(amount)
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        amount = Decimal(amount)
        amount_in_paise = int(amount * 100)

        order = client.order.create({
            "amount": int(amount_in_paise),  # paise
            "currency": "INR",
            "payment_capture": 1
        })

        return Response({
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": "INR"
        })

    except Exception as e:
        print(e)
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
import random
import string

def generate_random_alphanumeric(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_payment_and_create_appointment(request):

    try:
        data = request.data
        print(data)
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"],
        })
        
        room = generate_random_alphanumeric(10)
        
        patient_url = f"https://882cb53d146c.ngrok-free.app/peer1/{room}"
        doctor_url = f"https://882cb53d146c.ngrok-free.app/peer2/{room}"

        appointment = Appointment.objects.create(
            doctor_id=data["doctor_id"],
            patient=request.user,
            appointment_date=data["date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            amount=data["amount"],
            payment_status="paid",
            razorpay_order_id=data["razorpay_order_id"],
            razorpay_payment_id=data["razorpay_payment_id"],
            doctor_link=doctor_url,
            patient_link=patient_url
        )

        return Response(
            {
                "message": "Appointment booked successfully",
                "appointment_id": appointment.id
            },
            status=status.HTTP_201_CREATED
        )

    except razorpay.errors.SignatureVerificationError:
        return Response(
            {"message": "Payment verification failed"},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        print(e)
        return Response(
            {"message": "Something went wrong", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser, FormParser])
# def upload_transcription(request, appointment_id):

#     try:
#         appointment = Appointment.objects.get(
#             id=appointment_id,
#             doctor=request.user
#         )

#         appointment.transcription_file = request.FILES["file"]
#         appointment.status = "completed"
#         appointment.save()

#         return Response(
#             {"message": "Transcription uploaded successfully"},
#             status=status.HTTP_200_OK
#         )

#     except Appointment.DoesNotExist:
#         return Response(
#             {"message": "Appointment not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_booked_appointments(request):
    """
    Get appointments with status filter:
    - upcoming  -> booked + today/future
    - completed -> status = completed
    - cancelled -> status = cancelled
    - all       -> all appointments
    """

    user = request.user

    try:
        # ---------------- QUERY PARAM ----------------
        status_filter = request.GET.get("status", "all").lower()
        today = date.today()

        # ---------------- BASE QUERY ----------------
        try:
            if user.role == "patient":
                appointments = Appointment.objects.filter(patient=user)

            elif user.role == "doctor":
                appointments = Appointment.objects.filter(doctor=user)

            elif user.role == "admin":
                appointments = Appointment.objects.all()

            else:
                return Response(
                    {"message": "Unauthorized role"},
                    status=status.HTTP_403_FORBIDDEN
                )

        except Exception as e:
            return Response(
                {
                    "message": "Database error while fetching appointments",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ---------------- SEARCH FILTER ----------------
        try:
            if status_filter == "upcoming":
                # ✅ booked + today & future
                appointments = appointments.filter(
                    status="booked",
                    appointment_date__gte=today
                )

            elif status_filter == "completed":
                appointments = appointments.filter(
                    status="completed"
                )

            elif status_filter == "cancelled":
                appointments = appointments.filter(
                    status="cancelled"
                )

            elif status_filter == "all":
                pass  # no filter

            else:
                return Response(
                    {
                        "message": "Invalid status filter",
                        "allowed_values": [
                            "upcoming",
                            "completed",
                            "cancelled",
                            "all"
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {
                    "message": "Error while applying status filter",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ---------------- ORDERING ----------------
        appointments = appointments.order_by(
            "appointment_date", "start_time"
        )

        # ---------------- SERIALIZER ----------------
        serializer = AppointmentSerializer(
            appointments, many=True
        )

        return Response(
            {
                "message": "Appointments fetched successfully",
                "status_filter": status_filter,
                "count": appointments.count(),
                "appointments": serializer.data
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "message": "Unexpected error occurred",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(["POST"])
@permission_classes([AllowAny])
def get_or_create_prescription_by_doctor_link(request):

    doctor_link = request.data.get("doctor_link")
    diagnosis = request.data.get("diagnosis", "")
    additional_notes = request.data.get("additional_notes", "")
    medicines_data = request.data.get("medicines", [])

    if not doctor_link:
        return Response(
            {"error": "doctor_link is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔥 Normalize link
    doctor_link = doctor_link.rstrip("/")

    # 1️⃣ Fetch Appointment
    try:
        appointment = Appointment.objects.get(doctor_link=doctor_link)
    except Appointment.DoesNotExist:
        return Response(
            {"error": "Appointment not found for given doctor_link"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 🔐 Atomic transaction (safe)
    with transaction.atomic():

        # 2️⃣ Get or Create Prescription
        prescription, created = Prescription.objects.get_or_create(
            appointment=appointment
        )

        # 3️⃣ Update main prescription fields
        prescription.diagnosis = diagnosis
        prescription.additional_notes = additional_notes
        prescription.digital_signature = appointment.doctor.digital_signature_certificate
        prescription.save()

        # 4️⃣ Medicines handling
        if medicines_data:
            medicines_bulk = []
            for med in medicines_data:
                medicines_bulk.append(
                    PrescriptionMedicine(
                        prescription=prescription,
                        medicine_name=med.get("medicine_name"),
                        dose=med.get("dose"),
                        frequency=med.get("frequency"),
                        timing=med.get("timing"),
                        duration=med.get("duration"),
                    )
                )

            PrescriptionMedicine.objects.bulk_create(medicines_bulk)

    serializer = PrescriptionSerializer(prescription)

    return Response(
        {
            "created": created,
            "appointment_id": appointment.id,
            "prescription": serializer.data
        },
        status=status.HTTP_200_OK
    )  
    
@api_view(["POST"])
@permission_classes([AllowAny])
def upload_transcription_and_complete_appointment(request):
    """
    Body (multipart/form-data):
    - doctor_link OR patient_link
    - transcription_file (file)
    """

    link = request.data.get("link")
    transcription_file = request.FILES.get("transcription_file")

    if not link:
        return Response(
            {"error": "link is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔥 Normalize links (remove last /)
    if link:
        link = link.rstrip("/")
    
    try:
        appointment = Appointment.objects.get(doctor_link=link)
        
        if not appointment:
            appointment = Appointment.objects.get(patient_link=link)
        
    except Appointment.DoesNotExist:
        return Response(
            {"error": "Appointment not found for given link"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2️⃣ Save transcription file
    if transcription_file:
        appointment.transcription_file = transcription_file

    # 3️⃣ Mark appointment completed
    appointment.status = "completed"
    appointment.save()

    return Response(
        {
            "message": "Transcription uploaded & appointment completed",
            "appointment_id": appointment.id,
            "status": appointment.status,
            "transcription_file": appointment.transcription_file.url
        },
        status=status.HTTP_200_OK
    )



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def patient_appointments_with_prescription(request):
    user = request.user  # 👈 patient

    # 1️⃣ Fetch appointments of logged-in patient
    appointments = (
        Appointment.objects
        .filter(patient=user)
        .select_related("doctor", "patient")
        .prefetch_related("prescription__medicines")
        .order_by("-appointment_date", "-start_time")
    )

    response_data = []

    for appointment in appointments:
        appointment_data = AppointmentSerializer(appointment).data

        # 2️⃣ Try to fetch prescription
        prescription = getattr(appointment, "prescription", None)

        prescription_data = (
            PrescriptionSerializer(prescription).data
            if prescription else None
        )

        response_data.append({
            "appointment": appointment_data,
            "prescription": prescription_data
        })

    return Response(response_data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment
from Authentication.models import User
from .serializers import DoctorPatientSerializer

class DoctorPatientListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        patient_ids = Appointment.objects.filter(
            doctor_id=doctor_id
        ).values_list("patient_id", flat=True).distinct()

        patients = User.objects.filter(id__in=patient_ids)

        serializer = DoctorPatientSerializer(patients, many=True)
        return Response({
            "doctor_id": doctor_id,
            "total_patients": patients.count(),
            "patients": serializer.data
        })


class DoctorPatientPrescriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id, patient_id):
        prescriptions = Prescription.objects.filter(
            appointment__doctor_id=doctor_id,
            appointment__patient_id=patient_id
        ).select_related(
            "appointment"
        ).prefetch_related(
            "medicines"
        )

        serializer = PrescriptionSerializer(prescriptions, many=True)

        return Response({
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "total_prescriptions": prescriptions.count(),
            "prescriptions": serializer.data
        })
        
        
@api_view(["PUT"])
@permission_classes([AllowAny])
def update_prescription(request, prescription_id):

    diagnosis = request.data.get("diagnosis", "")
    additional_notes = request.data.get("additional_notes", "")
    medicines_data = request.data.get("medicines", [])

    # 1️⃣ Fetch Appointment
    try:
        prescription = Prescription.objects.get(id=prescription_id)
        appointment = prescription.appointment
    except Prescription.DoesNotExist:
        return Response(
            {"error": "Appointment not found for given doctor_link"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 🔐 Atomic transaction (safe)
    with transaction.atomic():

        # 3️⃣ Update main prescription fields
        prescription.diagnosis = diagnosis
        prescription.additional_notes = additional_notes
        prescription.digital_signature = appointment.doctor.digital_signature_certificate
        prescription.save()
        
        prescription.medicines.all().delete()

        # 4️⃣ Medicines handling
        if medicines_data:
            medicines_bulk = []
            for med in medicines_data:
                medicines_bulk.append(
                    PrescriptionMedicine(
                        prescription=prescription,
                        medicine_name=med.get("medicine_name"),
                        dose=med.get("dose"),
                        frequency=med.get("frequency"),
                        timing=med.get("timing"),
                        duration=med.get("duration"),
                    )
                )

            PrescriptionMedicine.objects.bulk_create(medicines_bulk)

    serializer = PrescriptionSerializer(prescription)

    return Response(
        {
            "appointment_id": appointment.id,
            "prescription": serializer.data
        },
        status=status.HTTP_200_OK
    )  