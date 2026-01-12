from django.db import models

# Create your models here.
class Appointment(models.Model):

    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    doctor = models.ForeignKey(
        'Authentication.User',
        on_delete=models.CASCADE,
        related_name="doctor_appointments"
    )

    patient = models.ForeignKey(
        'Authentication.User',
        on_delete=models.CASCADE,
        related_name="patient_appointments"
    )

    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="booked"
    )
    
    doctor_link = models.URLField(max_length=500, null=True, blank=True)
    patient_link = models.URLField(max_length=500, null=True, blank=True)
    # 💳 Payment fields
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
    )

    razorpay_order_id = models.CharField(
        max_length=200, blank=True, null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=200, blank=True, null=True
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    # 📝 Transcription after call
    transcription_file = models.FileField(
        upload_to="transcriptions/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "doctor",
            "appointment_date",
            "start_time"
        )

    def __str__(self):
        return f"{self.patient} → {self.doctor} | {self.appointment_date}"


class Prescription(models.Model):
    appointment = models.OneToOneField(
        "Appointment",
        on_delete=models.CASCADE,
        related_name="prescription"
    )

    diagnosis = models.TextField(null=True, blank=True)

    additional_notes = models.TextField(
        blank=True,
        null=True
    )

    digital_signature = models.FileField(
        upload_to="prescriptions/signatures/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for Appointment #{self.appointment.id}"
    

class PrescriptionMedicine(models.Model):

    FREQUENCY_CHOICES = [
        ("once", "Once a day"),
        ("twice", "Twice a day"),
        ("thrice", "Thrice a day"),
        ("sos", "SOS"),
    ]

    TIMING_CHOICES = [
        ("before_food", "Before Food"),
        ("after_food", "After Food"),
        ("empty_stomach", "Empty Stomach"),
    ]

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="medicines"
    )

    medicine_name = models.CharField(max_length=200)

    dose = models.CharField(
        max_length=100,
        help_text="e.g. 500mg, 1 tablet"
    )

    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES
    )

    timing = models.CharField(
        max_length=20,
        choices=TIMING_CHOICES,
        blank=True,
        null=True
    )

    duration = models.CharField(
        max_length=100,
        help_text="e.g. 5 days, 2 weeks"
    )

    def __str__(self):
        return f"{self.medicine_name} ({self.frequency})"
