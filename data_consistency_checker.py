#!/usr/bin/env python3
"""
Data Consistency Checker for Fees Management System
This script checks for and fixes data corruption issues automatically.
"""

import os
import django
from datetime import date, datetime
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings')
django.setup()

from core.models import Student, FeeDetails, FeeInstallments
from django.core.exceptions import ValidationError

class DataConsistencyChecker:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def log_issue(self, student_name, student_id, issue_type, description):
        """Log an issue found during checking"""
        self.issues_found.append({
            'student': student_name,
            'id': student_id,
            'type': issue_type,
            'description': description
        })
        
    def log_fix(self, student_name, student_id, fix_description):
        """Log a fix that was applied"""
        self.fixes_applied.append({
            'student': student_name,
            'id': student_id,
            'fix': fix_description
        })
    
    def check_fee_details(self):
        """Check FeeDetails table for data consistency issues"""
        print("🔍 Checking FeeDetails table...")
        
        fee_details = FeeDetails.objects.all()
        current_year = date.today().year
        
        for fee in fee_details:
            student_name = fee.registration_no.full_name
            student_id = fee.registration_no.registration_no
            
            # Check for negative amounts
            if fee.total_fees < 0:
                self.log_issue(student_name, student_id, "NEGATIVE_TOTAL", f"Total fees is negative: ₹{fee.total_fees}")
                
            if fee.fees_remaining < 0:
                self.log_issue(student_name, student_id, "NEGATIVE_REMAINING", f"Remaining fees is negative: ₹{fee.fees_remaining}")
                
            # Check if remaining > total
            if fee.fees_remaining > fee.total_fees:
                self.log_issue(student_name, student_id, "REMAINING_EXCEEDS_TOTAL", 
                             f"Remaining (₹{fee.fees_remaining}) > Total (₹{fee.total_fees})")
            
            # Check installment amounts
            installments = [
                ('first', fee.first_installment),
                ('second', fee.second_installment),
                ('third', fee.third_installment)
            ]
            
            for name, amount in installments:
                if amount and amount <= 0:
                    self.log_issue(student_name, student_id, "INVALID_INSTALLMENT_AMOUNT", 
                                 f"{name.title()} installment amount is invalid: ₹{amount}")
                    
                if amount and amount > fee.total_fees:
                    self.log_issue(student_name, student_id, "INSTALLMENT_EXCEEDS_TOTAL", 
                                 f"{name.title()} installment (₹{amount}) > Total fees (₹{fee.total_fees})")
            
            # Check installment dates
            dates = [
                ('first', fee.first_installment_date),
                ('second', fee.second_installment_date),
                ('third', fee.third_installment_date)
            ]
            
            for name, date_val in dates:
                if date_val:
                    # Check for invalid years (like 0025 instead of 2025)
                    if date_val.year < current_year - 1 or date_val.year > current_year + 10:
                        self.log_issue(student_name, student_id, "INVALID_DATE_YEAR", 
                                     f"{name.title()} installment date has invalid year: {date_val}")
    
    def check_fee_installments(self):
        """Check FeeInstallments table for data consistency issues"""
        print("🔍 Checking FeeInstallments table...")
        
        installments = FeeInstallments.objects.all()
        current_year = date.today().year
        
        for installment in installments:
            student_name = installment.registration_no.full_name
            student_id = installment.registration_no.registration_no
            
            # Check for negative or zero amounts
            if installment.amount <= 0:
                self.log_issue(student_name, student_id, "INVALID_INSTALLMENT_AMOUNT", 
                             f"Installment {installment.installment_no} has invalid amount: ₹{installment.amount}")
            
            # Check for unrealistic amounts (like 50000 instead of 5000)
            try:
                fee_details = installment.registration_no.feedetails
                if installment.amount > fee_details.total_fees:
                    self.log_issue(student_name, student_id, "INSTALLMENT_EXCEEDS_TOTAL", 
                                 f"Installment {installment.installment_no} (₹{installment.amount}) > Total fees (₹{fee_details.total_fees})")
            except FeeDetails.DoesNotExist:
                self.log_issue(student_name, student_id, "MISSING_FEE_DETAILS", 
                             f"No fee details found for installment {installment.installment_no}")
            
            # Check for invalid years in due dates
            if installment.due_date.year < current_year - 1 or installment.due_date.year > current_year + 10:
                self.log_issue(student_name, student_id, "INVALID_DUE_DATE_YEAR", 
                             f"Installment {installment.installment_no} has invalid due date year: {installment.due_date}")
            
            # Check for invalid installment numbers
            if installment.installment_no <= 0:
                self.log_issue(student_name, student_id, "INVALID_INSTALLMENT_NUMBER", 
                             f"Invalid installment number: {installment.installment_no}")
    
    def auto_fix_issues(self, apply_fixes=False):
        """Automatically fix common data corruption issues"""
        print("🔧 Checking for auto-fixable issues...")
        
        if not apply_fixes:
            print("   (Running in DRY RUN mode - no changes will be made)")
        
        # Fix FeeInstallments with corrupted data
        installments = FeeInstallments.objects.all()
        current_year = date.today().year
        
        for installment in installments:
            student_name = installment.registration_no.full_name
            student_id = installment.registration_no.registration_no
            fixed = False
            
            # Fix invalid years (0025 -> 2025, etc.)
            if installment.due_date.year < 1000:
                old_date = installment.due_date
                # Assume it should be 20XX instead of 00XX
                new_year = 2000 + (installment.due_date.year % 100)
                if new_year < current_year - 1:
                    new_year += 100  # Make it 21XX if too old
                
                new_date = installment.due_date.replace(year=new_year)
                
                if apply_fixes:
                    installment.due_date = new_date
                    installment.save()
                    fixed = True
                
                self.log_fix(student_name, student_id, 
                           f"Fixed due date: {old_date} → {new_date}")
            
            # Fix amounts that are clearly wrong (like 50000 instead of 5000)
            try:
                fee_details = installment.registration_no.feedetails
                if installment.amount > fee_details.total_fees * 2:  # Clearly wrong
                    old_amount = installment.amount
                    # Try to fix by removing extra zeros
                    new_amount = old_amount
                    while new_amount > fee_details.total_fees and new_amount > 10:
                        new_amount = new_amount / 10
                    
                    if new_amount <= fee_details.total_fees and new_amount >= 100:
                        if apply_fixes:
                            installment.amount = new_amount
                            installment.save()
                            fixed = True
                        
                        self.log_fix(student_name, student_id, 
                                   f"Fixed installment {installment.installment_no} amount: ₹{old_amount} → ₹{new_amount}")
            except FeeDetails.DoesNotExist:
                pass
    
    def generate_report(self):
        """Generate a comprehensive report"""
        print("\n" + "="*80)
        print("📊 DATA CONSISTENCY REPORT")
        print("="*80)
        
        if not self.issues_found and not self.fixes_applied:
            print("✅ No data consistency issues found!")
            return
        
        if self.issues_found:
            print(f"\n🚨 ISSUES FOUND: {len(self.issues_found)}")
            print("-" * 50)
            
            issue_types = {}
            for issue in self.issues_found:
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)
            
            for issue_type, issues in issue_types.items():
                print(f"\n{issue_type.replace('_', ' ').title()}: {len(issues)} issues")
                for issue in issues:
                    print(f"  • {issue['student']} (ID: {issue['id']}): {issue['description']}")
        
        if self.fixes_applied:
            print(f"\n✅ FIXES APPLIED: {len(self.fixes_applied)}")
            print("-" * 50)
            
            for fix in self.fixes_applied:
                print(f"  • {fix['student']} (ID: {fix['id']}): {fix['fix']}")
        
        print(f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run_full_check(self, apply_fixes=False):
        """Run complete data consistency check"""
        print("🚀 Starting Data Consistency Check...")
        print(f"Mode: {'FIX ISSUES' if apply_fixes else 'CHECK ONLY'}")
        print("-" * 50)
        
        self.check_fee_details()
        self.check_fee_installments()
        self.auto_fix_issues(apply_fixes)
        self.generate_report()
        
        return len(self.issues_found), len(self.fixes_applied)

def main():
    """Main function to run the data consistency checker"""
    checker = DataConsistencyChecker()
    
    print("Data Consistency Checker for Fees Management System")
    print("=" * 60)
    
    # First run in check-only mode
    print("\n1️⃣ Running initial check...")
    issues_count, _ = checker.run_full_check(apply_fixes=False)
    
    if issues_count > 0:
        print(f"\n⚠️  Found {issues_count} issues.")
        
        # Ask user if they want to apply auto-fixes
        response = input("\nDo you want to apply automatic fixes? (y/N): ").lower().strip()
        
        if response in ['y', 'yes']:
            print("\n2️⃣ Applying automatic fixes...")
            checker = DataConsistencyChecker()  # Reset for clean run
            checker.run_full_check(apply_fixes=True)
            print("\n✅ Fixes applied! Please refresh your browser to see changes.")
        else:
            print("\n⏭️  No fixes applied. Issues remain in the database.")
    
    print("\n🏁 Data consistency check completed!")

if __name__ == "__main__":
    main()
