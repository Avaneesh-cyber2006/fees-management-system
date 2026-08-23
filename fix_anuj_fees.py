import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings')
django.setup()

from core.models import Student, FeeDetails

# Find student Anuj
try:
    student = Student.objects.get(registration_no=102)
    print(f"Found student: {student.full_name}")
    
    # Get fee details
    fee_details = FeeDetails.objects.get(registration_no=student)
    print(f"\nCurrent Fee Details:")
    print(f"Total Fees: ₹{fee_details.total_fees}")
    print(f"Fees Remaining: ₹{fee_details.fees_remaining}")
    print(f"First Installment: ₹{fee_details.first_installment}")
    print(f"First Installment Date: {fee_details.first_installment_date}")
    print(f"Second Installment: ₹{fee_details.second_installment}")
    print(f"Second Installment Date: {fee_details.second_installment_date}")
    
    # Fix the issues
    print(f"\nFixing issues...")
    
    # Fix first installment amount (50000 -> 5000)
    if fee_details.first_installment == 50000:
        fee_details.first_installment = 5000
        print("✓ Fixed first installment amount: ₹50,000 → ₹5,000")
    
    # Fix first installment date (0025-10-27 -> 2025-10-27)
    if str(fee_details.first_installment_date).startswith('0025'):
        fee_details.first_installment_date = '2025-10-27'
        print("✓ Fixed first installment date: 0025-10-27 → 2025-10-27")
    
    # Save changes
    fee_details.save()
    print("\n✅ Changes saved successfully!")
    
    # Verify the fixes
    fee_details.refresh_from_db()
    print(f"\nUpdated Fee Details:")
    print(f"Total Fees: ₹{fee_details.total_fees}")
    print(f"Fees Remaining: ₹{fee_details.fees_remaining}")
    print(f"First Installment: ₹{fee_details.first_installment}")
    print(f"First Installment Date: {fee_details.first_installment_date}")
    print(f"Second Installment: ₹{fee_details.second_installment}")
    print(f"Second Installment Date: {fee_details.second_installment_date}")
    
except Student.DoesNotExist:
    print("Student with registration number 102 not found")
except FeeDetails.DoesNotExist:
    print("Fee details not found for this student")
except Exception as e:
    print(f"Error: {str(e)}")
