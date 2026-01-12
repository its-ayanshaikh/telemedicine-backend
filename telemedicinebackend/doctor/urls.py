"""
URL configuration for telemedicinebackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views  import *
from patient.views import DoctorPatientListAPIView, DoctorPatientPrescriptionAPIView, update_prescription

urlpatterns = [
    path('add-schedule/', create_individual_doctor_schedule, name="add_individual_doctor_schedule"),
    path('view-schedule/', get_individual_doctor_schedule, name="view_individual_doctor_schedule"),
    path('update-schedule/<int:schedule_id>/', update_individual_doctor_schedule, name="update_individual_doctor_schedule"),
    path('available-slots/<int:doctor_id>/', get_doctor_available_slots, name="get_doctor_available_slots"),
    path("<int:doctor_id>/patients/", DoctorPatientListAPIView.as_view(), name="doctor-patients"),
    path("<int:doctor_id>/patient/<int:patient_id>/prescriptions/", DoctorPatientPrescriptionAPIView.as_view(), name="doctor-patient-prescriptions"),
    path("prescription/<int:prescription_id>/update/", update_prescription, name="update-prescription")
    
]
