from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # ------------------ LIST PAGE CONFIG ----------------------
    list_display = (
        "id",
        "username",
        "first_name",
        "mobile_number",
        "email",
        "role",
        "status_badge",
        "is_active",
        "created_at",
    )

    list_filter = (
        "status",
        "role",
        "gender",
        "hospital_type",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "username",
        "mobile_number",
        "first_name",
        "last_name",
        "email",
        "hospital_name",
        "doctor_license_number",
        "registration_number",
    )

    ordering = ("-created_at",)
    
    # Per page
    list_per_page = 25

    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    )
    
    # ------------------ ACTIONS FOR BULK APPROVE/REJECT ----------------------
    actions = ["approve_users", "reject_users", "mark_pending"]
    
    @admin.action(description="✅ Approve selected users")
    def approve_users(self, request, queryset):
        count = queryset.update(status="approved")
        # Send emails for each user
        for user in queryset:
            from .email_service import send_status_email
            send_status_email(user, "approved")
        self.message_user(request, f"✅ {count} user(s) approved successfully!")
    
    @admin.action(description="❌ Reject selected users")
    def reject_users(self, request, queryset):
        count = queryset.update(status="rejected")
        # Send emails for each user
        for user in queryset:
            from .email_service import send_status_email
            send_status_email(user, "rejected")
        self.message_user(request, f"❌ {count} user(s) rejected!")
    
    @admin.action(description="⏳ Mark as Pending")
    def mark_pending(self, request, queryset):
        count = queryset.update(status="pending")
        self.message_user(request, f"⏳ {count} user(s) marked as pending!")
    
    # ------------------ STATUS BADGE DISPLAY ----------------------
    @admin.display(description="Status")
    def status_badge(self, obj):
        if obj.status == "approved":
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;">✓ Approved</span>'
            )
        elif obj.status == "rejected":
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;">✕ Rejected</span>'
            )
        elif obj.status == "pending":
            return format_html(
                '<span style="background-color: #f59e0b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;">⏳ Pending</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6b7280; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;">— Not Set</span>'
            )
    
    # ------------------ DEFAULT FILTER: SHOW DOCTORS ONLY ----------------------
    def changelist_view(self, request, extra_context=None):
        # If no role filter is applied, show Doctor + Hospital by default
        if 'role__exact' not in request.GET and 'role__in' not in request.GET and 'role' not in request.GET:
            q = request.GET.copy()
            q.setlist('role__in', ['doctor', 'hospital'])
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


    # ------------------ FIELDSETS (EDIT USER PAGE) ----------------------

    fieldsets = (

        (_("Login Credentials"), {
            "fields": (
                "username",
                "password",
                "mobile_number",
            )
        }),

        (_("Basic Personal Details"), {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "age",
                "gender",
            )
        }),

        (_("Role & Status"), {
            "fields": (
                "role",
                "status",
            )
        }),

        (_("Doctor Details"), {
            "fields": (
                "doctor_license_number",
                "specialization",
                "years_of_experience",
                "highest_qualification",
                "current_hospital",
                "degree_document",
                "other_certificate_document",
                "medical_license_document",
                "digital_signature_certificate",
                "consultation_fee",
            ),
            "classes": ("collapse",),
        }),

        (_("Hospital Details"), {
            "fields": (
                "hospital_name",
                "registration_number",
                "hospital_type",
                "hospital_address",
                "city",
                "state",
                "pincode",
                "hospital_digital_stamp",
            ),
            "classes": ("collapse",),
        }),

        (_("Hospital Admin Details"), {
            "fields": (
                "admin_name",
                "admin_phone_number",
            ),
            "classes": ("collapse",),
        }),

        (_("Address Proof & Documents"), {
            "fields": (
                "address_proof_document",
            ),
            "classes": ("collapse",),
        }),

        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        (_("Important Dates"), {
            "fields": (
                "last_login",
                "date_joined",
                "created_at",
                "updated_at",
            )
        }),
    )

    # ------------------ ADD USER PAGE (CREATE FORM) ----------------------

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "mobile_number",
                "password1",
                "password2",
                "first_name",
                "last_name",
                "email",
                "role",
            ),
        }),
    )

