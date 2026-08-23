import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings')
django.setup()

from core.models import Student, FeeDetails, FeeInstallments

print("="*80)
print("INSTALLMENTS TABLE ANALYSIS")
print("="*80)

# Check Anuj's data from both tables
try:
    anuj = Student.objects.get(registration_no=102)
    print(f"Student: {anuj.full_name} (ID: {anuj.registration_no})")
    
    # Check FeeDetails table
    print(f"\n{'='*50}")
    print("FEE DETAILS TABLE:")
    print(f"{'='*50}")
    
    fee_details = FeeDetails.objects.get(registration_no=anuj)
    print(f"Total Fees: ₹{fee_details.total_fees}")
    print(f"Fees Remaining: ₹{fee_details.fees_remaining}")
    print(f"Number of Installments: {fee_details.number_of_installments}")
    print(f"First Installment: ₹{fee_details.first_installment} (Due: {fee_details.first_installment_date})")
    print(f"Second Installment: ₹{fee_details.second_installment} (Due: {fee_details.second_installment_date})")
    if fee_details.third_installment:
        print(f"Third Installment: ₹{fee_details.third_installment} (Due: {fee_details.third_installment_date})")
    
    # Check FeeInstallments table
    print(f"\n{'='*50}")
    print("FEE INSTALLMENTS TABLE:")
    print(f"{'='*50}")
    
    installments = FeeInstallments.objects.filter(registration_no=anuj).order_by('installment_no')
    
    if installments.exists():
        print(f"Found {installments.count()} installment records:")
        for installment in installments:
            print(f"Installment {installment.installment_no}: ₹{installment.amount} (Due: {installment.due_date}) - Status: {installment.status}")
    else:
        print("No installment records found in FeeInstallments table")
    
    # Check which data source the template might be using
    print(f"\n{'='*50}")
    print("TEMPLATE DATA SOURCE ANALYSIS:")
    print(f"{'='*50}")
    
    # Check if the student detail view uses FeeInstallments
    print("The student detail template likely uses:")
    if installments.exists():
        print("- FeeInstallments table (newer system)")
        print("- This might be showing the old corrupted data")
    else:
        print("- FeeDetails table fields (older system)")
        print("- This should show the corrected data")

except Student.DoesNotExist:
    print("Student Anuj not found")
except FeeDetails.DoesNotExist:
    print("Fee details for Anuj not found")
except Exception as e:
    print(f"Error: {str(e)}")

# Check all installments in the system
print(f"\n{'='*80}")
print("ALL INSTALLMENTS IN SYSTEM:")
print(f"{'='*80}")

all_installments = FeeInstallments.objects.all().order_by('registration_no__registration_no', 'installment_no')
if all_installments.exists():
    for installment in all_installments:
        student_name = installment.registration_no.full_name
        print(f"{student_name} (ID: {installment.registration_no.registration_no}) - Installment {installment.installment_no}: ₹{installment.amount} (Due: {installment.due_date}) - {installment.status}")
else:
    print("No installments found in FeeInstallments table")
