from celery import shared_task
from django.core.mail import send_mail

from BMH import settings


@shared_task
def send_otp_mail(username,email,token):
    try:

        print(token)


        send_mail(
            subject='verification email for register as user in BMH',
            message= f" Hello {username}! Your verification code is {token}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        print(e)
@shared_task
def send_forgot_password_mail(email,content):
    try:
        send_mail(
            subject='forgot password email for register as user in BMH',
            message=content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )
    except Exception as e:
        print(e)

