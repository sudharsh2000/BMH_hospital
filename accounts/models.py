from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    role = models.CharField(max_length=100,choices=(('admin','admin'),('user','user'),('doctor','doctor')))
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.username


class OTP(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    otp = models.CharField(max_length=100)
    is_used= models.BooleanField(default=False)
    expired=models.DateTimeField()

