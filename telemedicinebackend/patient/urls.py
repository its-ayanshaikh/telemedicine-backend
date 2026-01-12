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


urlpatterns = [
    path('prescription/by-doctor-link/', get_or_create_prescription_by_doctor_link, name="get_or_create_prescription_by_doctor_link"),
    path('payments/create-order/', create_razorpay_order, name="create_razorpay_order"),
    path('payments/verify-payment/', verify_payment_and_create_appointment, name="verify_razorpay_payment"),
    path('complete/appointment/', upload_transcription_and_complete_appointment, name="upload_transcription_and_complete_appointment"),
    path('appointments/list/', get_booked_appointments, name="get_booked_appointments"),
    path("appointments-with-prescriptions/", patient_appointments_with_prescription, name="patient-appointments-with-prescriptions"),
]
