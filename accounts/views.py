from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema


from accounts.models import User
from django.db.models import Q
from django.shortcuts import render
from django.views import View
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from booking.serializers import DoctorSerializer
from accounts.models import OTP
from accounts.serializers import UserSerializer, VerifyOtpSerializer, ForgotPasswordSerializer, \
    ConfirmpasswordSerializer, ActivateDoctorSerializer, LoginSerializer,ResendOtpSerializer,VerifyOtpSerializer,ForgotPasswordSerializer,ConfirmpasswordSerializer
from accounts.services import AuthService
from booking.models import Doctor


# Create your views here.


class SignupView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class LoginView(APIView):
    @extend_schema(request=LoginSerializer, responses=LoginSerializer)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['login']
        password = serializer.data['password']
        
        user=User.objects.filter(Q(username=username) |Q(email=username)).first()
        if not user:
            return Response({'message': 'Invalid user Credentials'}, status=status.HTTP_404_NOT_FOUND)
        userval=authenticate(username=user.username, password=password)
        if userval:
            refresh=RefreshToken.for_user(user)

            if user.role =='doctor':
                doctor=Doctor.objects.get(user=user)
                serializer=DoctorSerializer(doctor,many=False)
                response = Response(
                    {"message": "success", "doctor":serializer.data, "user_id": user.id, "user_role": user.role, "name": user.username,
                     "access_token": str(refresh.access_token)}, status=status.HTTP_200_OK)

            else:
                response=Response({"message":"success","user_id":user.id,"user_role":user.role,"name":user.username, "access_token":str(refresh.access_token)},status=status.HTTP_200_OK)
            response.set_cookie('refresh_token', str(refresh), max_age=60*60*60*48,samesite='Lax',secure=True)
            return response
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
class LogoutView(APIView):
    serializer_class = None
    def post(self, request, *args, **kwargs):
        cookie=request.COOKIES.get('refresh_token')
        if cookie:
            response=Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            token=RefreshToken(cookie)
            token.blacklist()

            return response
        else:
            return Response({'message': 'Logout failed'}, status=status.HTTP_404_NOT_FOUND)
class RefreshTokenView(APIView):
    serializer_class=None
    def post(self, request, *args, **kwargs):

        refresh_cookie=request.COOKIES.get('refresh_token')
        if refresh_cookie:
            refresh=RefreshToken(refresh_cookie)
            response=Response({'message': 'Refresh successful','access_token':str(refresh.access_token)}, status=status.HTTP_200_OK)
            return response
        else:
            return Response({'message': 'Refresh failed'}, status=status.HTTP_404_NOT_FOUND)
class VerifyOtpView(APIView):
    @extend_schema(request=VerifyOtpSerializer, responses=VerifyOtpSerializer)
    def post(self, request, *args, **kwargs):

        serializer=VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data.get('user')
        otp_object=serializer.validated_data.get('otp_object')
        user.is_verified=True
        user.save()
        otp_object.is_used=True
        otp_object.save()
        return Response({'message': 'OTP verified'}, status=status.HTTP_201_CREATED)
class ResendOtpView(APIView):
    @extend_schema(request=ResendOtpSerializer, responses=ResendOtpSerializer)
    def post(self, request, *args, **kwargs):
        serializer=ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'OTP resended'}, status=status.HTTP_201_CREATED)
class ForgotPasswordView(APIView):
    @extend_schema(request=ForgotPasswordSerializer, responses=ForgotPasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer=ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data.get('user')
        uid,token=AuthService.forgot_password(user)
        return Response({'message': 'Forgot password successful','uid':uid,'token':token}, status=status.HTTP_200_OK)
class ConfirmPasswordView(APIView):
    @extend_schema(request=ConfirmpasswordSerializer,responses=ConfirmpasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer=ConfirmpasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({'message': 'Confirm password successful'}, status=status.HTTP_201_CREATED)





class setPasswordView(APIView):
    @extend_schema(request=ActivateDoctorSerializer,responses=ActivateDoctorSerializer)
    def post(self, request):
        serializer=ActivateDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data.get('user')
        password=serializer.validated_data.get('password')
        user.is_active = True
        user.set_password(password)
        user.save()
        return Response({"message":"Password set successfully"},status=200)

