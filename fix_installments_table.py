import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings')
django.setup()

from core.models import Student, FeeDetails, FeeInstallments

print("="*80)
print("FIXING INSTALLMENTS TABLE FOR ANUJ")
print("="*80)

try:
    anuj = Student.objects.get(registration_no=102)
    print(f"Found student: {anuj.full_name}")
    
    # Get current installments
    installments = FeeInstallments.objects.filter(registration_no=anuj).order_by('installment_no')
    
    print(f"\nCurrent installments:")
    for installment in installments:
        print(f"Installment {installment.installment_no}: ₹{installment.amount} (Due: {installment.due_date}) - Status: {installment.status}")
    
    # Fix the first installment
    first_installment = installments.filter(installment_no=1).first()
    if first_installment:
        print(f"\nFixing first installment...")
        print(f"Before: ₹{first_installment.amount} (Due: {first_installment.due_date})")
        
        # Fix the amount and date
        first_installment.amount = 5000.00  # Fix: 50000 -> 5000
        first_installment.due_date = '2025-10-27'  # Fix: 0025-10-27 -> 2025-10-27
        first_installment.status = 'Due'  # Change from Pending to Due
        first_installment.save()
        
        print(f"After: ₹{first_installment.amount} (Due: {first_installment.due_date}) - Status: {first_installment.status}")
        print("✅ First installment fixed!")
    
    # Verify the fix
    print(f"\n{'='*50}")
    print("VERIFICATION - Updated installments:")
    print(f"{'='*50}")
    
    updated_installments = FeeInstallments.objects.filter(registration_no=anuj).order_by('installment_no')
    for installment in updated_installments:
        print(f"Installment {installment.installment_no}: ₹{installment.amount} (Due: {installment.due_date}) - Status: {installment.status}")
    
    print(f"\n✅ Fix completed successfully!")
    print(f"Now the student detail page should show the correct values.")

except Student.DoesNotExist:
    print("Student Anuj not found")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
