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
    path('login/', login_user, name="login_user"),
    path('logout/', logout_user, name="logout_user"),
    path('profile/', profile_view, name="profile_view"),
    path('create-patient/', create_patient_user, name="create_patient_user"),
    path('create-doctor/', create_doctor_user, name="create_doctor_user"),
    path('get-doctor-list/', get_doctor_users, name="get_doctor_list"),
    path('create-hospital/', create_hospital_user, name="create_hospital_user"),
    path('verify-otp/', verify_otp_and_login, name="verify_otp"),
]
