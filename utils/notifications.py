import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from flask import current_app

class NotificationManager:
    def __init__(self):
        self.twilio_client = Client(
            current_app.config['TWILIO_ACCOUNT_SID'],
            current_app.config['TWILIO_AUTH_TOKEN']
        )
    
    def send_alert(self, analysis_results):
        self._send_email_alert(analysis_results)
        self._send_sms_alert(analysis_results)
    
    def _send_email_alert(self, analysis_results):
        msg = MIMEMultipart()
        msg['Subject'] = 'Crowd Alert!'
        msg['From'] = current_app.config['SMTP_USERNAME']
        
        body = f"""
        Crowd Alert at {analysis_results['timestamp']}!
        
        Current Statistics:
        - People Count: {analysis_results['count']}
        - Density: {analysis_results['density']:.2f}
        - Anomalies Detected: {len(analysis_results['anomalies'])}
        
        Please check the dashboard for more details.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(
            current_app.config['SMTP_SERVER'], 
            current_app.config['SMTP_PORT']
        ) as server:
            server.starttls()
            server.login(
                current_app.config['SMTP_USERNAME'],
                current_app.config['SMTP_PASSWORD']
            )
            
            for recipient in current_app.config['ALERT_EMAILS']:
                msg['To'] = recipient
                server.send_message(msg)
    
    def _send_sms_alert(self, analysis_results):
        message = f"""
        Crowd Alert!
        Count: {analysis_results['count']}
        Density: {analysis_results['density']:.2f}
        Time: {analysis_results['timestamp']}
        """
        
        for phone_number in current_app.config['ALERT_PHONE_NUMBERS']:
            self.twilio_client.messages.create(
                body=message,
                from_=current_app.config['TWILIO_PHONE_NUMBER'],
                to=phone_number
            )