import time
from datetime import  datetime, timedelta

from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.contrib.auth.hashers import make_password, check_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


from accounts.models import User
from rest_framework import serializers

from accounts.models import OTP
from accounts.services import AuthService
from accounts.tasks import send_otp_mail


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email','password']
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')


        user=User.objects.create_user(username=username, email=email, password=password)
        user.role='user'

        otp=AuthService.generate_otp()

        expired=timezone.now()+timedelta(minutes=5)

        send_otp_mail.delay(user.username,user.email,otp)


        otp_obj=OTP.objects.create(user=user,otp=make_password(str(otp)),expired=expired)
        otp_obj.save()

        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        if not User.objects.filter(email=email,is_verified=False).exists():
            raise serializers.ValidationError('User does not exist')
        try:
            user = User.objects.get(email=email, is_verified=False)
            if not OTP.objects.filter(user=user,is_used=False).exists():
                raise serializers.ValidationError('OTP does not exist')

            otp_object = OTP.objects.get(user=user,is_used=False)
            otp_check=check_password(otp,otp_object.otp)
            if not otp_check:
                raise serializers.ValidationError('Invalid OTP')
            if timezone.now()>otp_object.expired:
                raise serializers.ValidationError('OTP expired')
            attrs['otp_object']=otp_object
            attrs['user']=user
            return attrs
        except OTP.DoesNotExist:
            raise serializers.ValidationError('Invalid OTP')

class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate(self, attrs):
        if User.objects.filter(email=attrs['email'],is_verified=False).exists():
            raise serializers.ValidationError('please check your email')
        user = User.objects.get(email=attrs['email'],is_verified=False)
        if not OTP.objects.filter(user=user,is_used=False).exists():
            raise serializers.ValidationError('Otp already used')
        otp_object = OTP.objects.get(user=user,is_used=False)

        expired=timezone.now()+timedelta(minutes=5)
        token=AuthService.generate_otp()
        send_otp_mail.delay(user.username,user.email,otp_object.otp)
        otp_object.expired=expired
        otp_object.otp=make_password(token)
        otp_object.save()
        user.save()
        return attrs
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate(self, attrs):
        if not  User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError('User does not exist')
        user = User.objects.get(email=attrs['email'],is_verified=True)
        attrs['user']=user
        return attrs
class ConfirmpasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField()
    def validate(self, attrs):
        uid=attrs.get('uid')
        token=attrs.get('token')
        password = attrs.get('password')
        if not User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError('User does not exist')

        userid=force_str(urlsafe_base64_decode(uid))
        if not userid:
            raise serializers.ValidationError('Invalid uid')
        user = User.objects.get(email=attrs['email'])
        token_match=default_token_generator.check_token(user,token)
        if not token_match:
            raise serializers.ValidationError('Invalid token')

        attrs['user']=user
        return attrs


#for admin and doctor
class ActivateDoctorSerializer(serializers.Serializer):
    uid=serializers.CharField(max_length=80)
    token=serializers.CharField(max_length=80)
    password=serializers.CharField(max_length=80)
    email=serializers.EmailField(max_length=80)
    def validate(self,attrs):
        uid=attrs.get('uid')
        token=attrs.get('token')
        password=attrs.get('password')
        email=attrs.get('email')
        try:
            if not User.objects.filter(email=email).exists():
                raise ValidationError("Invalid email")


            uidmatch=force_str(urlsafe_base64_decode(uid))
            if not  User.objects.filter(pk=uidmatch).exists():
                raise ValidationError("Invalid user")

            user=User.objects.get(pk=uidmatch)
            if  user is None:
                raise ValidationError("Invalid uid")
            token_match=default_token_generator.check_token(user,token)
            if not token_match:
                raise ValidationError("Invalid token")
            if password is None or len(password)<8:
                raise ValidationError("Password does not meet the requirements")
        except ValidationError as e:
            raise ValidationError(e.args[0])

        attrs['user']=user

        return attrs