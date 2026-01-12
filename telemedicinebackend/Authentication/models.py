from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


def degree_upload_path(instance, filename):
    return f"users/{instance.username}/degree/{filename}"

def certificate_upload_path(instance, filename):
    return f"users/{instance.username}/certificates/{filename}"

def medical_license_upload_path(instance, filename):
    return f"users/{instance.username}/medical_license/{filename}"

def address_proof_upload_path(instance, filename):
    return f"users/{instance.username}/address_proof/{filename}"

def digital_signature_upload_path(instance, filename):
    return f"users/{instance.username}/digital_signature/{filename}"

def hospital_digital_stamp_upload_path(instance, filename):
    return f"users/{instance.username}/digital_stamp/{filename}"


GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]

HOSPITAL_TYPE_CHOICES = [
    ("private", "Private"),
    ("government", "Government"),
    ("semi_private", "Semi Private"),
    ("trust", "Trust"),
]

ROLE_CHOICES = [
    ("admin", "Admin"),
    ("doctor", "Doctor"),
    ("hospital", "Hospital"),
    ("patient", "Patient"),
    ("hospital-doctor", "Hospital Doctor"),
]



class User(AbstractUser):

    # 🔹 BASIC DETAILS
    mobile_number = models.CharField(max_length=15, unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        null=True,
        blank=True
    )

    # 🔹 DOCTOR DETAILS
    doctor_license_number = models.CharField(
        max_length=100, null=True, blank=True
    )
    specialization = models.CharField(
        max_length=150, null=True, blank=True
    )
    years_of_experience = models.PositiveIntegerField(
        null=True, blank=True
    )
    highest_qualification = models.CharField(
        max_length=150, null=True, blank=True
    )
    current_hospital = models.CharField(
        max_length=200, null=True, blank=True
    )

    degree_document = models.FileField(
        upload_to=degree_upload_path, null=True, blank=True
    )
    other_certificate_document = models.FileField(
        upload_to=certificate_upload_path, null=True, blank=True
    )
    medical_license_document = models.FileField(
        upload_to=medical_license_upload_path, null=True, blank=True
    )
    address_proof_document = models.FileField(
        upload_to=address_proof_upload_path, null=True, blank=True
    )
    digital_signature_certificate = models.FileField(
        upload_to=digital_signature_upload_path, null=True, blank=True
    )
    
    hospital_digital_stamp = models.FileField(
        upload_to=hospital_digital_stamp_upload_path, null=True, blank=True)

    # 🔹 HOSPITAL DETAILS
    hospital_name = models.CharField(
        max_length=200, null=True, blank=True
    )
    
    consultation_fee = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    registration_number = models.CharField(
        max_length=100, null=True, blank=True
    )
    hospital_type = models.CharField(
        max_length=20,
        choices=HOSPITAL_TYPE_CHOICES,
        null=True,
        blank=True
    )
    hospital_address = models.TextField(
        null=True, blank=True
    )
    city = models.CharField(
        max_length=100, null=True, blank=True
    )
    state = models.CharField(
        max_length=100, null=True, blank=True
    )
    pincode = models.CharField(
        max_length=10, null=True, blank=True
    )

    # 🔹 HOSPITAL ADMIN DETAILS
    admin_name = models.CharField(
        max_length=150, null=True, blank=True
    )
    admin_phone_number = models.CharField(
        max_length=15, null=True, blank=True
    )

    # 🔹 TIMESTAMPS
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending"
    )
    
    def __str__(self):
        return f"{self.username} - {self.role}"


# models.py



# Signal to send email when status changes
@receiver(pre_save, sender=User)
def send_status_change_email(sender, instance, **kwargs):
    """
    Send email when user status changes to 'approved' or 'rejected'
    """
    if instance.pk:  # Only for existing users (not new registrations)
        try:
            old_user = User.objects.get(pk=instance.pk)
            old_status = old_user.status
            new_status = instance.status
            
            # Check if status actually changed
            if old_status != new_status and new_status in ['approved', 'rejected']:
                # Import here to avoid circular imports
                from .email_service import send_status_email
                send_status_email(instance, new_status)
                print(f"Status changed from '{old_status}' to '{new_status}' for user {instance.username}")
        except User.DoesNotExist:
            pass  # New user, ignore

