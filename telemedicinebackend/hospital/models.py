from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL



class HospitalDoctor(models.Model):
    hospital = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hospital_doctors"
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_hospitals"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("hospital", "doctor")
        verbose_name = "Hospital Doctor"
        verbose_name_plural = "Hospital Doctors"

    def __str__(self):
        return f"{self.hospital} → {self.doctor}"



class HospitalDoctorSchedule(models.Model):

    DAYS = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    hospital_doctor = models.ForeignKey(
        HospitalDoctor,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ("hospital_doctor", "day", "start_time")

    def __str__(self):
        return f"{self.hospital_doctor} | {self.day} {self.start_time}-{self.end_time}"


class HospitalDoctorOff(models.Model):

    STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    hospital_doctor = models.ForeignKey(
        HospitalDoctor,
        on_delete=models.CASCADE,
        related_name="off_requests"
    )

    date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("hospital_doctor", "date")

    def __str__(self):
        return f"{self.hospital_doctor} | {self.date} ({self.status})"


class HospitalDoctorFee(models.Model):
    hospital_doctor = models.OneToOneField(
        HospitalDoctor,
        on_delete=models.CASCADE,
        related_name="fee"
    )

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.hospital_doctor} | ₹{self.amount}"
