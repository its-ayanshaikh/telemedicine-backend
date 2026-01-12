from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your models here.


class IndividualDoctorSchedule(models.Model):

    DAYS = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="individual_schedules"
    )

    date = models.DateField(null=True, blank=True)
    day = models.CharField(max_length=3, choices=DAYS)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    is_off = models.BooleanField(default=False)
    reason = models.TextField(blank=True)

    class Meta:
        unique_together = ("doctor", "date")

    def __str__(self):
        status = "OFF" if self.is_off else f"{self.start_time}-{self.end_time}"
        return f"{self.doctor} | {self.date} | {status}"



