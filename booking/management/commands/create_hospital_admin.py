from django.core.management import BaseCommand
from django.db.models import Q

from accounts.models import User
from booking.services import BookingService


class Command(BaseCommand):
    help = 'Create hospital admin account'
    def add_arguments(self, parser):
        parser.add_argument('--username',required=True)

        parser.add_argument('--email', required=True)
    def handle(self, *args, **options):

        if User.objects.filter(Q(username=options['username'])|Q(email=options['email'])).exists():
            return self.stdout.write(self.style.WARNING("User with this username already exists!"))
        user=User.objects.create_user(username=options['username'],email=options['email'],role='admin')
        user.set_unusable_password()
        user.save()
        uid,token=BookingService.doctor_account_activate(user)
        return self.stdout.write(self.style.SUCCESS(f"Created hospital admin account ! {uid}:{token}"))