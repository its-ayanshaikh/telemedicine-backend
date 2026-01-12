from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from django.db import IntegrityError
from .models import IndividualDoctorSchedule
from .serializers import *
from datetime import date, timedelta
from patient.models import Appointment

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_individual_doctor_schedule(request):

    user = request.user

    # 🔐 Role check
    if user.role != "doctor":
        return Response(
            {"message": "Only doctors can create schedules"},
            status=status.HTTP_403_FORBIDDEN
        )

    schedule_type = request.data.get("type")

    if schedule_type not in ["day", "weekly"]:
        return Response(
            {"message": "Invalid type. Use 'day' or 'weekly'"},
            status=status.HTTP_400_BAD_REQUEST
        )

    created_ids = []

    try:
        # ======================
        # 🟢 DAY-WISE
        # ======================
        if schedule_type == "day":

            if "date" not in request.data:
                return Response(
                    {"message": "date is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            date_obj = datetime.strptime(
                request.data["date"], "%Y-%m-%d"
            ).date()

            # ❌ duplicate check
            if IndividualDoctorSchedule.objects.filter(
                doctor=user, date=date_obj
            ).exists():
                return Response(
                    {
                        "message": "Schedule already exists for this date",
                        "date": str(date_obj)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            day_code = date_obj.strftime("%a").lower()[:3]
            is_off = request.data.get("is_off", False)

            payload = {
                "date": date_obj,
                "day": day_code,
                "is_off": is_off,
                "reason": request.data.get("reason", "")
            }

            if not is_off:
                if not request.data.get("start_time") or not request.data.get("end_time"):
                    return Response(
                        {"message": "start_time and end_time are required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                payload["start_time"] = datetime.strptime(
                    request.data["start_time"], "%I:%M %p"
                ).time()

                payload["end_time"] = datetime.strptime(
                    request.data["end_time"], "%I:%M %p"
                ).time()

            serializer = IndividualDoctorScheduleSerializer(data=payload)

            if serializer.is_valid():
                schedule = serializer.save(doctor=user)
                created_ids.append(schedule.id)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ======================
        # 🟢 WEEKLY
        # ======================
        else:
            days = request.data.get("days")

            if not isinstance(days, list) or not days:
                return Response(
                    {"message": "days list is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for item in days:
                date_obj = datetime.strptime(item["date"], "%Y-%m-%d").date()

                # ❌ duplicate date
                if IndividualDoctorSchedule.objects.filter(
                    doctor=user, date=date_obj
                ).exists():
                    return Response(
                        {
                            "message": "Schedule already exists for one or more dates",
                            "date": str(date_obj)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                day_code = date_obj.strftime("%a").lower()[:3]
                is_off = item.get("is_off", False)

                payload = {
                    "date": date_obj,
                    "day": day_code,
                    "is_off": is_off,
                    "reason": item.get("reason", "")
                }

                if not is_off:
                    if not item.get("start_time") or not item.get("end_time"):
                        return Response(
                            {
                                "message": "start_time and end_time required",
                                "date": str(date_obj)
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    payload["start_time"] = datetime.strptime(
                        item["start_time"], "%I:%M %p"
                    ).time()

                    payload["end_time"] = datetime.strptime(
                        item["end_time"], "%I:%M %p"
                    ).time()

                serializer = IndividualDoctorScheduleSerializer(data=payload)

                if serializer.is_valid():
                    schedule = serializer.save(doctor=user)
                    created_ids.append(schedule.id)
                else:
                    return Response(
                        serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {
                "message": "Schedule created successfully",
                "schedule_ids": created_ids
            },
            status=status.HTTP_201_CREATED
        )

    except IntegrityError:
        return Response(
            {"message": "Duplicate schedule detected"},
            status=status.HTTP_400_BAD_REQUEST
        )

    except ValueError as e:
        return Response(
            {
                "message": "Invalid date or time format",
                "error": str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {
                "message": "Something went wrong",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_individual_doctor_schedule(request):

    user = request.user

    if user.role != "doctor":
        return Response(
            {"message": "Only doctors can view their schedule"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        today = date.today()

        schedules = IndividualDoctorSchedule.objects.filter(
            doctor=user,
            date__gte=today   # ✅ today + future only
        ).order_by("date")

        serializer = IndividualDoctorScheduleSerializer(
            schedules, many=True
        )

        return Response(
            {
                "message": "Schedule fetched successfully",
                "count": schedules.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "message": "Something went wrong while fetching schedule",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_individual_doctor_schedule(request, schedule_id):

    user = request.user

    if user.role != "doctor":
        return Response(
            {"message": "Only doctors can update schedules"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        try:
            schedule = IndividualDoctorSchedule.objects.get(
                id=schedule_id,
                doctor=user   # 🔐 ownership check
            )
        except IndividualDoctorSchedule.DoesNotExist:
            return Response(
                {"message": "Schedule not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        update_data = {}

        # ✅ allowed fields only
        if "is_off" in request.data:
            update_data["is_off"] = request.data["is_off"]

        if "reason" in request.data:
            update_data["reason"] = request.data["reason"]

        if not request.data.get("is_off", False):
            if "start_time" in request.data:
                update_data["start_time"] = datetime.strptime(
                    request.data["start_time"], "%I:%M %p"
                ).time()

            if "end_time" in request.data:
                update_data["end_time"] = datetime.strptime(
                    request.data["end_time"], "%I:%M %p"
                ).time()

        serializer = IndividualDoctorScheduleSerializer(
            schedule,
            data=update_data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Schedule updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    except ValueError as e:
        return Response(
            {
                "message": "Invalid time format (use HH:MM AM/PM)",
                "error": str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {
                "message": "Something went wrong while updating schedule",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_doctor_available_slots(request, doctor_id):
    """
    Get doctor available slots (1-hour)
    Includes booked slots (marked unavailable)
    """

    try:
        today = date.today()

        # 🔍 Fetch doctor schedules (today + future, not off)
        schedules = IndividualDoctorSchedule.objects.filter(
            doctor_id=doctor_id,
            date__gte=today,
            is_off=False
        ).order_by("date", "start_time")

        if not schedules.exists():
            return Response(
                {
                    "message": "No available schedule found",
                    "slots": []
                },
                status=status.HTTP_200_OK
            )

        response_data = []

        for schedule in schedules:

            # 🔴 Fetch booked appointments for this doctor & date
            booked_appointments = Appointment.objects.filter(
                doctor_id=doctor_id,
                appointment_date=schedule.date,
                status="booked"
            )

            # 👉 Convert booked slots into set for fast lookup
            booked_slots = set()
            for appt in booked_appointments:
                booked_slots.add(
                    (
                        appt.start_time.strftime("%H:%M"),
                        appt.end_time.strftime("%H:%M")
                    )
                )

            day_slots = []

            start_dt = datetime.combine(schedule.date, schedule.start_time)
            end_dt = datetime.combine(schedule.date, schedule.end_time)

            while start_dt < end_dt:
                slot_end = start_dt + timedelta(hours=1)

                if slot_end <= end_dt:
                    slot_key = (
                        start_dt.strftime("%H:%M"),
                        slot_end.strftime("%H:%M")
                    )

                    is_available = slot_key not in booked_slots

                    day_slots.append({
                        "start_time": start_dt.strftime("%I:%M %p"),
                        "end_time": slot_end.strftime("%I:%M %p"),
                        "is_available": is_available
                    })

                start_dt = slot_end

            response_data.append({
                "date": schedule.date.strftime("%Y-%m-%d"),
                "day": schedule.get_day_display(),
                "slots": day_slots
            })

        return Response(
            {
                "message": "Doctor available slots fetched successfully",
                "doctor_id": doctor_id,
                "data": response_data
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "message": "Something went wrong while fetching slots",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
