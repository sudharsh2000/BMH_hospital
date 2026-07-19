from django.conf import settings
from celery import shared_task
from django.core.mail import send_mail
from BMH import settings
from booking.models import Appoinment


@shared_task
def send_Doctor_mail(email,content):

    try:
        send_mail(
            subject='To activate Your Account',
            message=content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )



    except Exception as e:
        print(e)
@shared_task
def send_appoinment_mail(email,username,doctorname,consult_time):
    try:

        send_mail(
            subject='Appoinment Booked',
            message=f" Dear {username} \n Your doctor appoinment is booked successfully to Dr {doctorname}.Appoinment scheduled at {consult_time}.Please  reach the hospital 10 minute before that "
                    f"\n\n Thank you BMH ",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )
    except Exception as e:
        print(e)


