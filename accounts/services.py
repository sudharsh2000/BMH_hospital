import uuid

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


from rest_framework.views import APIView
from random import randint

from BMH import settings
from accounts.tasks import send_forgot_password_mail


class AuthService:
    @staticmethod
    def generate_otp():
        otp=randint(100000,999999)
        return otp
    @staticmethod
    def generate_token_id(user):
        uid=urlsafe_base64_encode(force_bytes(user.pk))
        token=default_token_generator.make_token(user)
        return uid, token
    @staticmethod
    def forgot_password(user):
        print(user.pk)

        uid, token = AuthService.generate_token_id(user)
        link=f"{settings.FRONTEND_FORGOT_URL}/{uid}/{token}"
        message_content=f" This is the link for Your change password {link}"
        send_forgot_password_mail.delay(user.email, message_content)
        return uid,token
