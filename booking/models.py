from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.
from accounts.models import User
class Department(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Doctor(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_pics/',default='profile_pics/default.jpg')
    position = models.CharField(null=True,blank=True, max_length=100)
    experience = models.CharField(null=True,blank=True, max_length=100)
    fees=models.DecimalField(null=True,blank=True, max_digits=10,decimal_places=2,validators=[MinValueValidator(100.0),MaxValueValidator(10000.0)])
    specialization=models.ManyToManyField(Department,related_name='specialization')
    description=models.TextField()
    is_active = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username
class Timeslot(models.Model):
    doctor = models.ForeignKey(Doctor,related_name='time_slot', on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    available_day=models.IntegerField(null=True,blank=True,choices=((0,'Monday'),(1,'Tuesday'),(2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')))
    duration=models.IntegerField(null=True,blank=True,default=30,choices=((15,'15 minutes'), (30,'30 minutes'),(60,'60 minutes'),(90,'90 minutes')))
    is_confirmed = models.BooleanField(default=False)
    def __str__(self):
        return self.doctor.user.username

class Appoinment(BaseModel):
    doctor = models.ForeignKey(Doctor,related_name='booking', on_delete=models.CASCADE)
    slot_date=models.DateField(null=True,blank=True)
    slot_time=models.TimeField(null=True,blank=True)
    patient = models.ForeignKey(User,related_name='patient_booking',on_delete=models.SET_NULL,null=True)
    disease=models.TextField(null=True,blank=True)
    mobile_number=models.CharField(null=True,blank=True, max_length=10)
    previous_visit=models.BooleanField(default=False)
    status=models.CharField(null=True,blank=True, max_length=100,choices=(('pending','Pending'),('confirmed','Confirmed'),('rejected','Rejected')))
    reviewed_by=models.ForeignKey(User,related_name='reviewed_booking',on_delete=models.SET_NULL,null=True)
    def __str__(self):
        return self.doctor.user.username
    class Meta:
        unique_together = ('doctor','slot_date','slot_time')

class LeaveRequest(BaseModel):
    doctor = models.ForeignKey(Doctor,related_name='leave_request', on_delete=models.CASCADE)
    leave_date=models.DateField(null=True,blank=True)
    reason=models.TextField(null=True,blank=True)
    status=models.CharField(null=True,blank=True, max_length=100,choices=(('pending','Pending'), ('accepted','Accepted'),('rejected','Rejected')))
    def __str__(self):
        return self.doctor.user.username
class DoctorLeave(BaseModel):
    doctor = models.ForeignKey(Doctor,related_name='leave', on_delete=models.CASCADE)
    leave_date=models.DateField(null=True,blank=True)
    reason=models.TextField(null=True,blank=True)
    reviewed_by=models.ForeignKey(User,related_name='reviewed_leave',on_delete=models.SET_NULL,null=True)
class Prescription(BaseModel):
    appoinments=models.OneToOneField(Appoinment,related_name='prescription',on_delete=models.CASCADE)
    patient=models.ForeignKey(User,related_name='prescription',on_delete=models.SET_NULL,null=True)
    doctor=models.ForeignKey(Doctor,related_name='prescription',on_delete=models.SET_NULL,null=True)
    findings=models.TextField(null=True,blank=True)

    def __str__(self):
        return self.appoinment.user.username
class PrescriptionMedicine(BaseModel):
    prescriptions=models.ForeignKey(Prescription,related_name='prescription_item',on_delete=models.CASCADE)
    medicine=models.TextField(null=True,blank=True)
    dose=models.CharField(max_length=100,null=True,blank=True,help_text="eg:500 mg")
    routine=models.CharField(max_length=100,null=True,blank=True,choices=(('before food','before food'),('after food','after food')))
    dose_time=ArrayField(models.CharField(max_length=100,choices=(('morning','morning'),('after noon','after noon'),('night','night'))),null=True,blank=True,default=list,help_text="['morning'],['afternoon','evening']")
    no_of_days=models.IntegerField(null=True,blank=True,default=1)
    quantity=models.IntegerField(null=True,blank=True,default=1)
    def __str__(self):
        return self.prescription.user.username

