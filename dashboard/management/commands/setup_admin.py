from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import UserProfile

class Command(BaseCommand):
    help = 'Setup admin user profile'

    def handle(self, *args, **options):
        try:
            # Get the admin user
            admin_user = User.objects.get(username='admin_besant')
            
            # Create or update user profile
            profile, created = UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={'user_type': 'admin'}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('Successfully created admin profile for admin_besant')
                )
            else:
                profile.user_type = 'admin'
                profile.save()
                self.stdout.write(
                    self.style.SUCCESS('Successfully updated admin profile for admin_besant')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Admin user "admin_besant" not found. Please create a superuser first.')
            ) 