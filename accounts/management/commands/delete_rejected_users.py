from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import UserApproval


class Command(BaseCommand):
    help = 'Delete rejected users after 24 hours of rejection'

    def handle(self, *args, **options):
        # Calculate the time 24 hours ago
        time_threshold = timezone.now() - timedelta(hours=24)
        
        # Find all rejected users whose rejection_date is older than 24 hours
        rejected_users = UserApproval.objects.filter(
            status='rejected',
            rejection_date__lte=time_threshold
        )
        
        deleted_count = 0
        for approval in rejected_users:
            username = approval.user.username
            try:
                # Delete the user (this will cascade delete related objects)
                approval.user.delete()
                deleted_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Deleted rejected user: {username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error deleting user {username}: {str(e)}')
                )
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully deleted {deleted_count} rejected user(s) after 24 hours.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No rejected users eligible for deletion yet.')
            )
