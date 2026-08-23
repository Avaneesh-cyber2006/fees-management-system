import os
import django
from datetime import datetime, date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings')
django.setup()

from core.models import Student, FeeDetails

print("="*80)
print("COMPREHENSIVE STUDENT DATA ANALYSIS")
print("="*80)

# Get all students
all_students = Student.objects.all()
print(f"Total students in system: {all_students.count()}\n")

issues_found = []
today = date.today()

for student in all_students:
    print(f"\n{'='*50}")
    print(f"Student: {student.full_name} (ID: {student.registration_no})")
    print(f"{'='*50}")
    
    # Check fee details
    try:
        fee_details = FeeDetails.objects.get(registration_no=student)
        
        # Basic fee info
        print(f"Total Fees: ₹{fee_details.total_fees}")
        print(f"Fees Remaining: ₹{fee_details.fees_remaining}")
        print(f"Number of Installments: {fee_details.number_of_installments}")
        
        # Check for potential issues
        student_issues = []
        
        # Check installment amounts
        if hasattr(fee_details, 'first_installment') and fee_details.first_installment:
            print(f"First Installment: ₹{fee_details.first_installment} (Due: {fee_details.first_installment_date})")
            
            # Check for unrealistic amounts (like 50000 instead of 5000)
            if fee_details.first_installment > fee_details.total_fees:
                student_issues.append(f"First installment (₹{fee_details.first_installment}) exceeds total fees (₹{fee_details.total_fees})")
            
            # Check for date issues (year starting with 00)
            if str(fee_details.first_installment_date).startswith('00'):
                student_issues.append(f"First installment date has invalid year: {fee_details.first_installment_date}")
        
        if hasattr(fee_details, 'second_installment') and fee_details.second_installment:
            print(f"Second Installment: ₹{fee_details.second_installment} (Due: {fee_details.second_installment_date})")
            
            if fee_details.second_installment > fee_details.total_fees:
                student_issues.append(f"Second installment (₹{fee_details.second_installment}) exceeds total fees (₹{fee_details.total_fees})")
                
            if str(fee_details.second_installment_date).startswith('00'):
                student_issues.append(f"Second installment date has invalid year: {fee_details.second_installment_date}")
        
        if hasattr(fee_details, 'third_installment') and fee_details.third_installment:
            print(f"Third Installment: ₹{fee_details.third_installment} (Due: {fee_details.third_installment_date})")
            
            if fee_details.third_installment > fee_details.total_fees:
                student_issues.append(f"Third installment (₹{fee_details.third_installment}) exceeds total fees (₹{fee_details.total_fees})")
                
            if str(fee_details.third_installment_date).startswith('00'):
                student_issues.append(f"Third installment date has invalid year: {fee_details.third_installment_date}")
        
        # Check payment status vs dates
        if fee_details.fees_remaining > 0:
            # Check if any installment is overdue
            installment_dates = []
            if hasattr(fee_details, 'first_installment_date') and fee_details.first_installment_date:
                installment_dates.append(fee_details.first_installment_date)
            if hasattr(fee_details, 'second_installment_date') and fee_details.second_installment_date:
                installment_dates.append(fee_details.second_installment_date)
            if hasattr(fee_details, 'third_installment_date') and fee_details.third_installment_date:
                installment_dates.append(fee_details.third_installment_date)
            
            overdue_dates = [d for d in installment_dates if d < today]
            if overdue_dates:
                print(f"⚠️  OVERDUE: {len(overdue_dates)} installment(s) past due date")
                for overdue_date in overdue_dates:
                    days_overdue = (today - overdue_date).days
                    print(f"   - {overdue_date} ({days_overdue} days overdue)")
            else:
                print(f"✅ CURRENT: Next due date is in the future")
        
        # Add issues to global list
        if student_issues:
            issues_found.extend([(student.full_name, student.registration_no, issue) for issue in student_issues])
            print(f"\n🚨 ISSUES FOUND:")
            for issue in student_issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ No data issues found")
            
    except FeeDetails.DoesNotExist:
        issue = "No fee details found"
        issues_found.append((student.full_name, student.registration_no, issue))
        print(f"🚨 {issue}")

# Summary
print(f"\n\n{'='*80}")
print("SUMMARY REPORT")
print(f"{'='*80}")

if issues_found:
    print(f"🚨 TOTAL ISSUES FOUND: {len(issues_found)}")
    print("\nDetailed Issues:")
    for name, reg_no, issue in issues_found:
        print(f"  • {name} (ID: {reg_no}): {issue}")
else:
    print("✅ No data issues found in any student records")

print(f"\nAnalysis completed on {today}")
