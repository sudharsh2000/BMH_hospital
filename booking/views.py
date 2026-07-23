from datetime import timezone, datetime

from django.core.cache import cache
from django.shortcuts import render, get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView, Response

from booking.models import Department, Doctor, Timeslot, Appoinment, Prescription
from booking.serializers import DepartmentSerializer, DoctorSerializer, CreateDoctorSerializer, UpdateDoctorSerializer, \
    TimeslotSerializer, TakeAppoinmentSerializer, GetAppointmentSerializer, GetPrescriptionSerializer, \
    AddPrescriptionSerializer, ProfileImageSerializer, getTimeslotDateSerializer, verifyAppoinmentSerializer
from booking.services import BookingService
from booking.tasks import send_appoinment_mail
from managementapp.permissions import Hr, ISDoctor, IsUser


# Create your views here.
class DepartmentView(ListCreateAPIView):
    permission_classes = [Hr]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DoctorViewset(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'],permission_classes=[Hr])
    def activate(self,request,pk=None):
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor.is_active = True
        doctor.save()
        return Response({"message": "Activate Doctor"}, status=status.HTTP_200_OK)
    @action(detail=True, methods=['post'],permission_classes=[Hr])
    def deactivate(self,request,pk=None):
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor.is_active = False
        doctor.save()
        return  Response({"message":"Deactivate Doctor"}, status=status.HTTP_200_OK)
    @extend_schema(request=ProfileImageSerializer,responses=ProfileImageSerializer)
    @action(detail=True, methods=['post'],parser_classes=[MultiPartParser,FormParser],permission_classes=[Hr])
    def upload_image(self,request,pk=None):
        serializer = ProfileImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = Doctor.objects.get(pk=pk)
        profile_image = serializer.data['profile_image']

        doctor.profile_image = profile_image
        doctor.save()
        return Response({"message":"Image uploaded"})

    @action(detail=True, methods=['post'],permission_classes=[Hr])
    def Confirm_Timeslot(self,request,pk=None):
        doctor = get_object_or_404(Doctor, pk=pk)
        timeslot=Timeslot.objects.filter(doctor=doctor,is_confirmed=False)
        for timeslot in timeslot:
            timeslot.is_confirmed = True
            timeslot.save()
        return Response({'Timeslot approves':timeslot.values()})
    @action(detail=False, methods=['get'],permission_classes=[Hr])
    def get_pending_timeslots(self,request,pk=None):
        slot = Doctor.objects.filter(is_active=True).prefetch_related('time_slot').all()
        serializer = DoctorSerializer(slot, many=True)
        return Response({'timeslot':serializer.data})
    @extend_schema(request=getTimeslotDateSerializer,responses=getTimeslotDateSerializer)
    @action(detail=True, methods=['get'])
    def get_timeslots(self,request,pk=None):

        doctor=self.get_object()

        serializers=getTimeslotDateSerializer(data=request.data)

        serializers.is_valid(raise_exception=True)
        select_date=serializers.data['selected_date']
        available_slots=BookingService.get_available_slots(doctor, select_date)
        return Response({'available_slots':available_slots})

    def get_queryset(self):
        if self.action in ('update','partial_update'):
            return Doctor.objects.all()
        return Doctor.objects.filter(is_active=True)
    def get_serializer_class(self):

        if self.action == 'create':
            return CreateDoctorSerializer
        elif self.action == 'update' or self.action == 'partial_update':

            return UpdateDoctorSerializer

        return  DoctorSerializer


    def get_permissions(self):

        if self.action == 'create':
            return [Hr()]
        elif self.action == 'update' or self.action == 'partial_update':
            return [ISDoctor()]
        return [AllowAny()]
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['specialization__name','user__username','position']
    search_fields = ['specialization__name','user__username','position']
    ordering_fields = ['specialization__name','user__username','position']


class TakeAppoinmentViewSet(viewsets.ModelViewSet):
    queryset = Appoinment.objects.all()
    serializer_class = TakeAppoinmentSerializer

    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['status','disease']

    @action(detail=True, methods=['post'],permission_classes=[Hr])
    def verify_appointment(self,request,pk=None):
        appoinment=self.get_object()
        serializers=verifyAppoinmentSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        appoinment.status=serializers.validated_data['status']
        appoinment.verified_by=request.user
        appoinment.updated_at=datetime.now()
        appoinment.save()
        return Response({'message':'Appointment verified'})

    def get_queryset(self):
        user=self.request.user

        if user.role=='doctor':
            return Appoinment.objects.filter(doctor=user).select_related('patient')
        if user.role=='patient':
            return Appoinment.objects.filter(patient=user).select_related('doctor')
        return Appoinment.objects.all().select_related('patient','doctor')

    def get_serializer_class(self):
        if self.action == 'create':
            return TakeAppoinmentSerializer
        return GetAppointmentSerializer
    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
        doctor=serializer.validated_data['doctor']
        email=self.request.user.email
        print(email,doctor.user.username)
        send_appoinment_mail.delay(self.request.user.email,self.request.user.username, doctor.user.username,datetime.combine(serializer.validated_data['slot_date'], serializer.validated_data['slot_time']))
        return Response({'message':'Appoinment created'},status=status.HTTP_201_CREATED)


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all().select_related('doctor','patient','appoinments')
    serializers=GetPrescriptionSerializer(queryset,many=True)

    @action(detail=False, methods=['post'],permission_classes=[IsUser])
    def get_my_prescriptions(self,request):
        queryset=Prescription.objects.filter(patients=self.request.user).select_related('doctor','patient','appoinments')
        serializers=GetPrescriptionSerializer(queryset,many=True)
        return Response({'data':serializers.data},status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'create':
            return AddPrescriptionSerializer
        return GetPrescriptionSerializer
    def get_permissions(self):
        if self.action == 'create':
            return [ISDoctor()]
        return [IsAuthenticated()]
    def perform_create(self, serializer):
        doctor=Doctor.objects.get(user=self.request.user)
        serializer.save(doctor=doctor)