import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fees_management_system.settings')
django.setup()

from core.models import Student, FeeDetails

# Search for student Anuj
students = Student.objects.filter(first_name__icontains='anuj')
print(f"Students found with name containing 'anuj': {students.count()}")

for student in students:
    print(f"\nStudent Details:")
    print(f"Registration No: {student.registration_no}")
    print(f"Name: {student.full_name}")
    print(f"Date of Birth: {student.date_of_birth}")
    print(f"Gender: {student.gender}")
    
    # Check fee details
    try:
        fee_details = FeeDetails.objects.get(registration_no=student)
        print(f"\nFee Details:")
        print(f"Total Fees: ₹{fee_details.total_fees}")
        print(f"Fees Remaining: ₹{fee_details.fees_remaining}")
        print(f"Number of Installments: {fee_details.number_of_installments}")
        print(f"Fees per Installment: ₹{fee_details.fees_per_installment}")
        
        # Check installment details
        if hasattr(fee_details, 'first_installment') and fee_details.first_installment:
            print(f"First Installment: ₹{fee_details.first_installment} (Due: {fee_details.first_installment_date})")
        if hasattr(fee_details, 'second_installment') and fee_details.second_installment:
            print(f"Second Installment: ₹{fee_details.second_installment} (Due: {fee_details.second_installment_date})")
        if hasattr(fee_details, 'third_installment') and fee_details.third_installment:
            print(f"Third Installment: ₹{fee_details.third_installment} (Due: {fee_details.third_installment_date})")
            
    except FeeDetails.DoesNotExist:
        print("No fee details found for this student")

# Also search by last name or registration number
print("\n" + "="*50)
print("Searching by last name 'anuj':")
students_lastname = Student.objects.filter(last_name__icontains='anuj')
print(f"Students found: {students_lastname.count()}")

print("\n" + "="*50)
print("All students in the system:")
all_students = Student.objects.all()
for student in all_students:
    print(f"ID: {student.registration_no}, Name: {student.full_name}")
