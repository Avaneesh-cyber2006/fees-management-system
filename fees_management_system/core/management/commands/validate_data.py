from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from core.models import Student, FeeDetails, FeeInstallments
from datetime import date

class Command(BaseCommand):
    help = 'Validate and fix data consistency issues in the fees management system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Apply automatic fixes to data issues',
        )
        parser.add_argument(
            '--student-id',
            type=int,
            help='Check specific student by registration number',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting data validation...')
        )
        
        issues_found = 0
        fixes_applied = 0
        
        # Filter students if specific ID provided
        if options['student_id']:
            try:
                students = [Student.objects.get(registration_no=options['student_id'])]
                self.stdout.write(f"Checking student ID: {options['student_id']}")
            except Student.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Student with ID {options["student_id"]} not found')
                )
                return
        else:
            students = Student.objects.all()
            self.stdout.write(f"Checking all {students.count()} students...")
        
        for student in students:
            student_issues = self.validate_student(student, options['fix'])
            issues_found += student_issues['issues']
            fixes_applied += student_issues['fixes']
        
        # Summary
        self.stdout.write("\n" + "="*50)
        if issues_found == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No data issues found!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Found {issues_found} issues')
            )
            
        if fixes_applied > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Applied {fixes_applied} fixes')
            )
        
        self.stdout.write("🏁 Data validation completed!")
    
    def validate_student(self, student, apply_fixes=False):
        """Validate a single student's data"""
        issues = 0
        fixes = 0
        
        self.stdout.write(f"\n🔍 Checking {student.full_name} (ID: {student.registration_no})")
        
        # Check FeeDetails
        try:
            fee_details = FeeDetails.objects.get(registration_no=student)
            fee_issues, fee_fixes = self.validate_fee_details(fee_details, apply_fixes)
            issues += fee_issues
            fixes += fee_fixes
        except FeeDetails.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('  ❌ No fee details found')
            )
            issues += 1
        
        # Check FeeInstallments
        installments = FeeInstallments.objects.filter(registration_no=student)
        for installment in installments:
            inst_issues, inst_fixes = self.validate_installment(installment, apply_fixes)
            issues += inst_issues
            fixes += inst_fixes
        
        if issues == 0:
            self.stdout.write('  ✅ No issues found')
        
        return {'issues': issues, 'fixes': fixes}
    
    def validate_fee_details(self, fee_details, apply_fixes=False):
        """Validate FeeDetails record"""
        issues = 0
        fixes = 0
        
        try:
            fee_details.full_clean()
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ FeeDetails.{field}: {error}')
                    )
                    issues += 1
        
        return issues, fixes
    
    def validate_installment(self, installment, apply_fixes=False):
        """Validate FeeInstallments record"""
        issues = 0
        fixes = 0
        current_year = date.today().year
        
        # Check for invalid year in due date
        if installment.due_date.year < 1000:
            old_date = installment.due_date
            new_year = 2000 + (installment.due_date.year % 100)
            if new_year < current_year - 1:
                new_year += 100
            
            new_date = installment.due_date.replace(year=new_year)
            
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  Invalid due date year: {old_date}')
            )
            issues += 1
            
            if apply_fixes:
                installment.due_date = new_date
                installment.save()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Fixed due date: {old_date} → {new_date}')
                )
                fixes += 1
        
        # Check for unrealistic amounts
        try:
            fee_details = installment.registration_no.feedetails
            if installment.amount > fee_details.total_fees * 2:
                old_amount = installment.amount
                new_amount = old_amount
                
                # Try to fix by removing extra zeros
                while new_amount > fee_details.total_fees and new_amount > 10:
                    new_amount = new_amount / 10
                
                if new_amount <= fee_details.total_fees and new_amount >= 100:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  Unrealistic amount: ₹{old_amount}')
                    )
                    issues += 1
                    
                    if apply_fixes:
                        installment.amount = new_amount
                        installment.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Fixed amount: ₹{old_amount} → ₹{new_amount}')
                        )
                        fixes += 1
        except FeeDetails.DoesNotExist:
            pass
        
        # Validate using model's clean method
        try:
            installment.full_clean()
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Installment {installment.installment_no}.{field}: {error}')
                    )
                    issues += 1
        
        return issues, fixes
