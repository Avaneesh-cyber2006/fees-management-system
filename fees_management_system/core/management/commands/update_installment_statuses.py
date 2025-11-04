from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import FeeInstallments
from datetime import date


class Command(BaseCommand):
    help = 'Update installment statuses from Due to Pending for overdue payments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"🔄 Starting installment status update - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("🧪 DRY RUN MODE - No changes will be made")
            )
        
        try:
            # Get overdue installments that are still marked as 'Due'
            today = date.today()
            overdue_installments = FeeInstallments.objects.filter(
                due_date__lt=today,
                status='Due'
            ).select_related('registration_no')
            
            total_overdue = overdue_installments.count()
            
            if total_overdue == 0:
                self.stdout.write(
                    self.style.SUCCESS("✅ No overdue installments found. All statuses are up to date!")
                )
                return
            
            self.stdout.write(f"📊 Found {total_overdue} overdue installments to update")
            
            if verbose or dry_run:
                self.stdout.write("\n📋 Overdue installments details:")
                for installment in overdue_installments:
                    days_overdue = (today - installment.due_date).days
                    self.stdout.write(
                        f"  • {installment.registration_no.full_name} "
                        f"(Reg: {installment.registration_no.registration_no}) - "
                        f"Installment {installment.installment_no} - "
                        f"₹{installment.amount} - "
                        f"{days_overdue} days overdue"
                    )
            
            if not dry_run:
                # Update statuses
                updated_count = overdue_installments.update(
                    status='Pending',
                    updated_at=timezone.now()
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Successfully updated {updated_count} installments to 'Pending' status"
                    )
                )
                
                # Log the update
                self.log_update(updated_count, overdue_installments)
                
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"🧪 Would update {total_overdue} installments to 'Pending' status"
                    )
                )
            
            # Show summary statistics
            self.show_statistics()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error updating installment statuses: {str(e)}")
            )
            raise
    
    def log_update(self, updated_count, installments):
        """Log the update to a file"""
        try:
            import os
            from datetime import datetime
            
            # Ensure logs directory exists
            os.makedirs('logs', exist_ok=True)
            
            log_file = 'logs/installment_status_updates.log'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Installment Status Update - {timestamp} ===\n")
                f.write(f"Updated {updated_count} installments to 'Pending' status\n")
                
                for installment in installments:
                    days_overdue = (date.today() - installment.due_date).days
                    f.write(
                        f"- {installment.registration_no.full_name} "
                        f"(Reg: {installment.registration_no.registration_no}) - "
                        f"Installment {installment.installment_no} - "
                        f"₹{installment.amount} - {days_overdue} days overdue\n"
                    )
                f.write("=" * 50 + "\n")
            
            self.stdout.write(f"📝 Update logged to: {log_file}")
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Could not write to log file: {str(e)}")
            )
    
    def show_statistics(self):
        """Show current installment statistics"""
        try:
            stats = {
                'total': FeeInstallments.objects.count(),
                'due': FeeInstallments.objects.filter(status='Due').count(),
                'pending': FeeInstallments.objects.filter(status='Pending').count(),
                'paid': FeeInstallments.objects.filter(status='Paid').count(),
            }
            
            self.stdout.write("\n📊 Current Installment Statistics:")
            self.stdout.write(f"  Total Installments: {stats['total']}")
            self.stdout.write(f"  Due: {stats['due']}")
            self.stdout.write(f"  Pending: {stats['pending']}")
            self.stdout.write(f"  Paid: {stats['paid']}")
            
            # Calculate percentages
            if stats['total'] > 0:
                due_pct = (stats['due'] / stats['total']) * 100
                pending_pct = (stats['pending'] / stats['total']) * 100
                paid_pct = (stats['paid'] / stats['total']) * 100
                
                self.stdout.write(f"\n📈 Percentage Distribution:")
                self.stdout.write(f"  Due: {due_pct:.1f}%")
                self.stdout.write(f"  Pending: {pending_pct:.1f}%")
                self.stdout.write(f"  Paid: {paid_pct:.1f}%")
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Could not generate statistics: {str(e)}")
            )
