from django.db.models.signals import post_delete
from django.dispatch import receiver

from booking.models import Timeslot, Doctor


@receiver(post_delete, sender=Doctor)
def delete_doctor(sender, instance, **kwargs):
    print(instance.user)
    instance.user.delete()

    timeslot=Timeslot.objects.filter(doctor_id=instance.id)
    timeslot.delete()
    print("deleted doctor {}".format(instance))