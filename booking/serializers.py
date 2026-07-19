from django.contrib.auth import validators
from django.contrib.auth.tokens import default_token_generator
import django.contrib.auth.password_validation as validators
from django.db import transaction
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from accounts.models import User
from accounts.serializers import UserSerializer
from booking.models import Department, Doctor, Timeslot, Appoinment, Prescription, PrescriptionMedicine
from booking.services import BookingService


# complete department
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id','name']

    def validate_name(self, name):
        print('name',name)
        if Department.objects.filter(name=name).exists():
            raise ValidationError('Department with this name already exists')
        return name



# Time slot


# create doctor by admin
class CreateDoctorSerializer(serializers.ModelSerializer):
    username=serializers.CharField(max_length=80,write_only=True)
    email=serializers.CharField(max_length=80,write_only=True)
    specialization=serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), write_only=True,many=True)

    class Meta:
        model = Doctor
        fields=['username','email','specialization','description','position','fees']

    def validate_fees(self,value):
        if value < 0:
            raise serializers.ValidationError('Fees must be greater than 100')
        if value > 10000:
            raise serializers.ValidationError('Fees must be less than 10000')
        return value

    def create(self,validated_data):

        username=validated_data.pop('username')
        email=validated_data.pop('email')
        specialization=validated_data.pop('specialization')
        user=User.objects.create_user(username=username,email=email,role='doctor')
        user.set_unusable_password()
        user.save()
        uid,token=BookingService.doctor_account_activate(user)
        doctor=Doctor.objects.create(user=user,fees=int(validated_data['fees']), description=validated_data.get('description'),position=validated_data.get('position'))
        doctor.specialization.set(specialization)
        doctor.save()
        validated_data['uid']=uid
        validated_data['token']=token


        return doctor
class TimeslotSerializer(serializers.ModelSerializer):
    available_day_display=serializers.CharField(source='get_available_day_display',read_only=True)
    available_day=serializers.IntegerField(write_only=True)


    class Meta:
        model = Timeslot
        fields = ['id', 'start_time', 'end_time', 'available_day','available_day_display']
        read_only_fields = ['id']
# update doctor by doctor
class UpdateDoctorSerializer(serializers.ModelSerializer):
    time_slots= TimeslotSerializer(many=True,write_only=True)

    class Meta:
        model = Doctor
        fields = ['experience','time_slots']
    @transaction.atomic
    def update(self,instance,validated_data):

        time_slots=validated_data.pop('time_slots')


        instance.experience=validated_data.get('experience')
        instance.is_profile_complete=True
        instance.save()
        Timeslot.objects.filter(doctor=instance.id).delete()

        Timeslot.objects.bulk_create([Timeslot(doctor=instance, **slot) for slot in time_slots])

        return instance

#get doctor
class DoctorSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    time_slot=serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['id', 'user','profile_image','position','experience','specialization','description','fees','time_slot']
    def get_time_slot(self,doctor):
        queryset=[ts for ts in doctor.time_slot.all()]
        return TimeslotSerializer(queryset,many=True).data

#image upload serializer
class ProfileImageSerializer(serializers.Serializer):
    profile_image=serializers.ImageField()

class getTimeslotDateSerializer(serializers.Serializer):
    selected_date=serializers.DateField()



class TakeAppoinmentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Appoinment
        fields=['doctor','slot_date','slot_time','disease','mobile_number','previous_visit']
        read_only_fields = ['id','status','verified by','created_at','updated_at']


class GetAppointmentSerializer(serializers.ModelSerializer):
    patient=UserSerializer(read_only=True)
    doctor=DoctorSerializer(read_only=True)
    class Meta:
        model=Appoinment
        fields=['patient','doctor','slot_date','slot_time','disease','mobile_number','previous_visit']

class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model=PrescriptionMedicine
        fields=['medicine','dose','routine', 'dose_time','no_of_days','quantity']

class AddPrescriptionSerializer(serializers.ModelSerializer):
    medicines=PrescriptionMedicineSerializer(PrescriptionMedicine.objects.all(), many=True,write_only=True)
    class Meta:
        model=Prescription
        fields=['appoinments','patient','findings','medicines']
    def create(self,validated_data):
        medicines=validated_data.pop('medicines')
        prescriptions=Prescription.objects.create(**validated_data)
        print(medicines)

        PrescriptionMedicine.objects.bulk_create([PrescriptionMedicine(prescriptions=prescriptions,medicine=med['medicine'],dose=med['dose'],routine=med['routine'],no_of_days=med['no_of_days'],quantity=med['quantity'],dose_time=med['dose_time']) for med in medicines])
        return prescriptions
class GetPrescriptionSerializer(serializers.ModelSerializer):
    medicine=serializers.SerializerMethodField()
    appoinments=GetAppointmentSerializer(read_only=True)

    class Meta:
        model=Prescription
        fields=['id', 'appoinments','findings','medicine']
    def get_medicine(self,prescription):
        queryset=[ts for ts in prescription.prescription_item.all()]
        return PrescriptionMedicineSerializer(queryset,many=True).data

class verifyAppoinmentSerializer(serializers.Serializer):
    status=serializers.CharField()