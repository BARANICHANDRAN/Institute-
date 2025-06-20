from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import UserProfile, Student, Task, TaskSubmission

class Command(BaseCommand):
    help = 'Clear all users except admin_besant and related data.'

    def handle(self, *args, **options):
        # Keep only the admin user
        admin_username = 'admin_besant'
        try:
            admin_user = User.objects.get(username=admin_username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Admin user "{admin_username}" not found.'))
            return

        # Delete all other users and their profiles
        UserProfile.objects.exclude(user=admin_user).delete()
        Student.objects.all().delete()
        TaskSubmission.objects.all().delete()
        Task.objects.all().delete()
        User.objects.exclude(username=admin_username).delete()

        self.stdout.write(self.style.SUCCESS('Database cleared except for admin user and profile.')) 