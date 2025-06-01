# a_users/management/commands/cleanup_deactivated_accounts.py

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from a_users.models import Profile
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Permanently delete accounts that have been deactivated for more than 30 days'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=Profile.REACTIVATION_GRACE_PERIOD_DAYS,
            help=f'Number of days after deactivation to delete accounts (default: {Profile.REACTIVATION_GRACE_PERIOD_DAYS})',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of accounts to process in each batch (default: 100)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )
    
    def handle(self, *args, **options):
        try:
            days = options['days']
            batch_size = options['batch_size']
            dry_run = options['dry_run']
            force = options['force']
            
            cutoff_date = timezone.now() - timedelta(days=days)
            
            # Find profiles that are permanently deactivated
            profiles_to_delete = Profile.objects.filter(
                user__is_active=False,
                deactivated_at__lt=cutoff_date
            ).select_related('user')
            
            count = profiles_to_delete.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS('No accounts found for deletion.')
                )
                return
            
            # Show what will be deleted
            self.stdout.write(
                self.style.WARNING(f'Found {count} accounts deactivated for more than {days} days')
            )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('DRY RUN - No accounts will be deleted')
                )
                self._show_accounts_to_delete(profiles_to_delete[:10])  # Show first 10
                if count > 10:
                    self.stdout.write(f'... and {count - 10} more accounts')
                return
            
            # Confirmation prompt (unless --force is used)
            if not force:
                confirm = input(f'\nAre you sure you want to permanently delete {count} accounts? [y/N]: ')
                if confirm.lower() not in ['y', 'yes']:
                    self.stdout.write('Operation cancelled.')
                    return
            
            # Delete accounts in batches
            self._delete_accounts_in_batches(profiles_to_delete, batch_size)
            
        except Exception as e:
            logger.error(f'Error in cleanup command: {str(e)}')
            raise CommandError(f'Command failed: {str(e)}')
    
    def _show_accounts_to_delete(self, profiles):
        """Display accounts that would be deleted"""
        self.stdout.write('\nAccounts to be deleted:')
        for profile in profiles:
            deactivated_days = (timezone.now() - profile.deactivated_at).days
            self.stdout.write(
                f'  - {profile.user.username} (ID: {profile.user.id}) '
                f'- deactivated {deactivated_days} days ago'
            )
    
    def _delete_accounts_in_batches(self, profiles_queryset, batch_size):
        """Delete accounts in batches to avoid memory issues"""
        deleted_count = 0
        total_count = profiles_queryset.count()
        
        self.stdout.write(f'\nDeleting {total_count} accounts in batches of {batch_size}...')
        
        # Process in batches
        for i in range(0, total_count, batch_size):
            batch = list(profiles_queryset[i:i + batch_size])
            
            try:
                with transaction.atomic():
                    deleted_users = []
                    
                    for profile in batch:
                        username = profile.user.username
                        user_id = profile.user.id
                        
                        # Log before deletion
                        logger.info(f'Permanently deleting user {username} (ID: {user_id})')
                        
                        # Delete user (cascades to profile)
                        profile.user.delete()
                        deleted_users.append(username)
                    
                    deleted_count += len(deleted_users)
                    
                    # Progress update
                    self.stdout.write(
                        f'Batch {i//batch_size + 1}: Deleted {len(deleted_users)} accounts '
                        f'({deleted_count}/{total_count} total)'
                    )
                    
            except Exception as e:
                logger.error(f'Error deleting batch {i//batch_size + 1}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(f'Error in batch {i//batch_size + 1}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully deleted {deleted_count} permanently deactivated accounts')
        )
        
        if deleted_count < total_count:
            self.stdout.write(
                self.style.WARNING(f'Warning: {total_count - deleted_count} accounts could not be deleted')
            )