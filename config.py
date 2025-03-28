import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/crowd_analysis')
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    ALERT_PHONE_NUMBERS = os.getenv('ALERT_PHONE_NUMBERS', '').split(',')
    ALERT_EMAILS = os.getenv('ALERT_EMAILS', '').split(',')
    CROWD_THRESHOLD = int(os.getenv('CROWD_THRESHOLD', 50))
    DENSITY_THRESHOLD = float(os.getenv('DENSITY_THRESHOLD', 0.7))