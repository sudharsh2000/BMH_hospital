from rest_framework.response import Response

from BMH import settings

from accounts.services import AuthService
from booking.models import Doctor, DoctorLeave, Timeslot, Appoinment
from booking.tasks import send_Doctor_mail
from datetime import datetime, timedelta


class BookingService:
    @staticmethod
    def doctor_account_activate(user):


        uid,token=AuthService.generate_token_id(user)
        link=f"{settings.FRONTEND_ACTIVATE_URL}/{uid}/{token}"
        content=f" Welcome {user.role} {user.username}  to BMH \n Please activate your account using this link: {link}"
        send_Doctor_mail.delay(user.email, content)
        return uid, token
    @staticmethod
    def get_available_slots(doctor,selected_date):

        if DoctorLeave.objects.filter(doctor=doctor,leave_date=selected_date).exists():
            return []
        weekday=datetime.strptime( selected_date,"%Y-%m-%d").date().weekday()
        print(doctor)
        if not Timeslot.objects.filter(available_day=weekday,doctor=doctor).exists():
            return []
        all_available_slots=[]
        timeslot=Timeslot.objects.get(available_day=weekday,doctor=doctor)
        start=datetime.combine(datetime.today(),timeslot.start_time)
        end=datetime.combine(datetime.today(),timeslot.end_time)
        duration=timedelta(minutes=timeslot.duration)
        while start+duration <= end:
            all_available_slots.append(start.time())
            start+=duration

        already_slot=Appoinment.objects.filter(doctor=doctor,slot_date=selected_date,status__in=('pending','confirmed')).values('slot_time')
        available_slots=[ s for s in all_available_slots if s not in already_slot]
        return available_slots
