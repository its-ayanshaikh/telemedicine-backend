from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        feilds = "__all__"

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_active",
        )
        



class CreatePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "age",
            "mobile_number",
            "gender",
        )
        
    

    def create(self, validated_data):
        # 🔐 role hardcoded
        validated_data["role"] = "patient"
        
        validated_data["username"] = validated_data["mobile_number"]


        # 🔑 password blank / unusable (OTP based login)
        user = User(**validated_data)
        user.set_unusable_password()
        user.save()

        return user
    

class CreateDoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "mobile_number",
            "email",

            "doctor_license_number",
            "specialization",
            "years_of_experience",
            "highest_qualification",
            "consultation_fee",
            "degree_document",
            "other_certificate_document",
            "medical_license_document",
            "address_proof_document",
            "digital_signature_certificate",
        )

    def create(self, validated_data):
        # 🔹 Role hardcoded
        validated_data["role"] = "doctor"
        
        validated_data["username"] = validated_data["mobile_number"]


        # 🔹 Password generate: firstname + lastname + @123
        first_name = validated_data.get("first_name", "").lower()
        last_name = validated_data.get("last_name", "").lower()
        raw_password = f"{first_name}{last_name}@123"

        # 🔹 User create
        user = User(**validated_data)
        user.set_password(raw_password)  # 🔐 hash
        user.save()

        # 🔥 password return ke liye context me save
        self.context["generated_password"] = raw_password

        return user
    
class DoctorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "mobile_number",
            "email",
            "role",
            "consultation_fee",
            "hospital_type",
            "hospital_address",
            "doctor_license_number",
            "specialization",
            "years_of_experience",
            "highest_qualification",
            "current_hospital",

            "degree_document",
            "other_certificate_document",
            "medical_license_document",
            "address_proof_document",
            "digital_signature_certificate",

            "created_at",
        )

    
class CreateHospitalSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "hospital_name",
            "registration_number",
            "hospital_type",

            "mobile_number",
            "email",

            "hospital_address",
            "city",
            "state",
            "pincode",

            "admin_name",
            "admin_phone_number",
            
            "hospital_digital_stamp",
        )

    def create(self, validated_data):
        # 🔹 role hardcoded
        validated_data["role"] = "hospital"
        
        validated_data["username"] = validated_data["mobile_number"]


        # 🔹 password generate: hospitalname@123
        hospital_name = validated_data.get("hospital_name", "")
        cleaned_name = hospital_name.replace(" ", "").lower()
        raw_password = f"{cleaned_name}@123"

        # 🔹 create user
        user = User(**validated_data)
        user.set_password(raw_password)  # 🔐 hash password
        user.save()

        # 🔥 dev/testing ke liye context me store
        self.context["generated_password"] = raw_password

        return user

