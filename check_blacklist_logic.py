import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings')
django.setup()

from core.models import Student, FeeDetails

print("="*80)
print("BLACKLIST LOGIC ANALYSIS")
print("="*80)

today = date.today()
print(f"Today's date: {today}")
print(f"Today is: {today.strftime('%A, %B %d, %Y')}")

# Check Anuj specifically
try:
    anuj = Student.objects.get(registration_no=102)
    fee_details = FeeDetails.objects.get(registration_no=anuj)
    
    print(f"\n{'='*50}")
    print(f"ANUJ'S BLACKLIST STATUS ANALYSIS")
    print(f"{'='*50}")
    
    print(f"Student: {anuj.full_name}")
    print(f"Fees Remaining: ₹{fee_details.fees_remaining}")
    print(f"Total Fees: ₹{fee_details.total_fees}")
    
    print(f"\nInstallment Details:")
    print(f"First Installment: ₹{fee_details.first_installment} (Due: {fee_details.first_installment_date})")
    print(f"Second Installment: ₹{fee_details.second_installment} (Due: {fee_details.second_installment_date})")
    
    # Check each installment date
    installment_dates = [
        ("First", fee_details.first_installment_date),
        ("Second", fee_details.second_installment_date),
        ("Third", fee_details.third_installment_date)
    ]
    
    print(f"\nDate Analysis:")
    overdue_found = False
    for name, due_date in installment_dates:
        if due_date:
            days_diff = (due_date - today).days
            if due_date < today:
                print(f"  {name} Installment: {due_date} - ❌ OVERDUE by {abs(days_diff)} days")
                overdue_found = True
            elif due_date == today:
                print(f"  {name} Installment: {due_date} - ⚠️  DUE TODAY")
            else:
                print(f"  {name} Installment: {due_date} - ✅ Due in {days_diff} days")
    
    # Check the is_overdue property
    print(f"\nBlacklist Logic Check:")
    print(f"Fees Remaining > 0: {fee_details.fees_remaining > 0}")
    print(f"Is Overdue (model property): {fee_details.is_overdue}")
    print(f"Should be blacklisted: {fee_details.is_overdue and fee_details.fees_remaining > 0}")
    
    # Manual check of the logic
    manual_overdue = False
    if fee_details.fees_remaining > 0:
        for name, due_date in installment_dates:
            if due_date and due_date < today:
                manual_overdue = True
                break
    
    print(f"Manual overdue check: {manual_overdue}")
    
    if fee_details.is_overdue and not overdue_found:
        print(f"\n🚨 ISSUE: Student marked as overdue but no overdue dates found!")
    elif not fee_details.is_overdue and overdue_found:
        print(f"\n🚨 ISSUE: Student has overdue dates but not marked as overdue!")
    else:
        print(f"\n✅ Blacklist logic is working correctly")

except Student.DoesNotExist:
    print("Student Anuj not found")
except FeeDetails.DoesNotExist:
    print("Fee details for Anuj not found")

# Check all students for blacklist status
print(f"\n{'='*80}")
print("ALL STUDENTS BLACKLIST STATUS")
print(f"{'='*80}")

all_students = Student.objects.all()
blacklisted_count = 0

for student in all_students:
    try:
        fee_details = FeeDetails.objects.get(registration_no=student)
        is_blacklisted = fee_details.is_overdue and fee_details.fees_remaining > 0
        
        if is_blacklisted:
            blacklisted_count += 1
            print(f"❌ {student.full_name} (ID: {student.registration_no}) - BLACKLISTED")
            
            # Show why they're blacklisted
            installment_dates = [
                fee_details.first_installment_date,
                fee_details.second_installment_date,
                fee_details.third_installment_date
            ]
            
            for due_date in installment_dates:
                if due_date and due_date < today:
                    days_overdue = (today - due_date).days
                    print(f"   Overdue installment: {due_date} ({days_overdue} days ago)")
        else:
            print(f"✅ {student.full_name} (ID: {student.registration_no}) - NOT BLACKLISTED")
            
    except FeeDetails.DoesNotExist:
        print(f"⚠️  {student.full_name} (ID: {student.registration_no}) - NO FEE DETAILS")

print(f"\nSummary: {blacklisted_count} out of {all_students.count()} students are blacklisted")
