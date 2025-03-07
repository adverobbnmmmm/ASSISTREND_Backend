import random
from django.core.mail import send_mail
from django.conf import settings
import boto3
from twilio.rest import Client  # Import Twilio
from django.core.cache import cache  # Import cache
from decouple import config 


# Twilio credentials (Get these from Twilio console)
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER")

def generateOtp(length=6):
    return str(random.randint(111111, 999999))  # Generate a 6-digit OTP

def sendOtpEmail(email, otp):
    subject = "Your OTP Code"
    message = f"Your OTP is: {otp}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

def sendOtpSMS(phone, otp):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # Ensure phone number is in E.164 format
    if not phone.startswith("+"):
        phone = "+91" + phone  # Add country code (Modify based on your region)
    message = client.messages.create(
        body=f"Your OTP code is {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )
    return message.sid

# "for production purposes for a large scale"
# def send_otp_sms(phone_number, otp):
#     client = boto3.client(
#         "sns",
#         region_name="us-east-1",  # Change to your preferred region
#         aws_access_key_id="YOUR_ACCESS_KEY",
#         aws_secret_access_key="YOUR_SECRET_KEY",
#     )
#     message = f"Your OTP code is: {otp}"
    
#     response = client.publish(
#         PhoneNumber=phone_number,  # Example: "+919876543210"
#         Message=message,
#     )
    
#     return response
