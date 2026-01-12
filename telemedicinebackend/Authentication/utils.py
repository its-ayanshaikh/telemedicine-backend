from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
from django.conf import settings
import random

import redis

# Redis connection
# def get_redis_client():
#     # Password None ho to without password connect hoga
#     redis_config = {
#         "host": settings.REDIS_HOST,
#         "port": settings.REDIS_PORT,
#         "db": settings.REDIS_DB,
#         "decode_responses": True
#     }
    
#     # Only add password if it exists
#     if settings.REDIS_PASSWORD:
#         redis_config["password"] = settings.REDIS_PASSWORD
    
#     return redis.Redis(**redis_config)
def get_redis_client():
    return redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    
    
def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp_in_redis(user_id, otp):
    """
    Store OTP in Redis with 5 min expiry
    Key format: otp:{user_id}
    """
    redis_client = get_redis_client()
    key = f"otp:{user_id}"
    redis_client.setex(key, settings.OTP_EXPIRY_SECONDS, otp)
    print(f"OTP stored in Redis for user {user_id}, expires in {settings.OTP_EXPIRY_SECONDS} seconds")

def verify_otp_from_redis(user_id, otp_entered):
    """
    Verify OTP from Redis
    Returns: (success: bool, message: str)
    """
    redis_client = get_redis_client()
    key = f"otp:{user_id}"
    
    stored_otp = redis_client.get(key)
    
    if stored_otp is None:
        return False, "OTP expired or not found"
    
    if stored_otp != otp_entered:
        return False, "Invalid OTP"
    
    # OTP verified, delete it
    redis_client.delete(key)
    return True, "OTP verified successfully"

def delete_otp_from_redis(user_id):
    """
    Delete OTP from Redis (after successful verification or manual delete)
    """
    redis_client = get_redis_client()
    key = f"otp:{user_id}"
    redis_client.delete(key)

def send_otp_twilio(otp, mobile_number):
    """
    DEV MODE:
    OTP hamesha verified number par jayega
    """
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )
    
    if not mobile_number.startswith("+"):
        mobile_number = "+91" + mobile_number

    message = client.messages.create(
        body=f"Your login OTP is {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=mobile_number # 👈 VERIFIED NUMBER ONLY
    )

    return message.sid
