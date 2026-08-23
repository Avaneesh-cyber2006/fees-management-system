from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Student, ParentInfo, Branch, AcademicInfo, FeeDetails
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))
        
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
        
        # Create branches
        branches_data = [
            {'branch_code': 'MAIN', 'branch_name': 'Main Branch', 'branch_location': 'Central Mumbai'},
            {'branch_code': 'ANDHERI', 'branch_name': 'Andheri Branch', 'branch_location': 'Andheri West'},
            {'branch_code': 'BANDRA', 'branch_name': 'Bandra Branch', 'branch_location': 'Bandra East'},
        ]
        
        for branch_data in branches_data:
            branch, created = Branch.objects.get_or_create(
                branch_code=branch_data['branch_code'],
                defaults=branch_data
            )
            if created:
                self.stdout.write(f'Created branch: {branch.branch_name}')
        
        # Sample student data
        students_data = [
            {
                'registration_no': 1001,
                'first_name': 'Arjun',
                'last_name': 'Sharma',
                'gender': 'M',
                'father_name': 'Rajesh Sharma',
                'father_mobile': '9876543210',
                'mother_mobile': '9876543211',
                'course': 'ICSE Class 10',
                'total_fees': 50000,
                'fees_remaining': 20000,
            },
            {
                'registration_no': 1002,
                'first_name': 'Sneha',
                'last_name': 'Patel',
                'gender': 'F',
                'father_name': 'Amit Patel',
                'father_mobile': '9876543212',
                'mother_mobile': '9876543213',
                'course': 'ICSE Class 9',
                'total_fees': 45000,
                'fees_remaining': 15000,
            },
            {
                'registration_no': 1003,
                'first_name': 'Rohan',
                'last_name': 'Kumar',
                'gender': 'M',
                'father_name': 'Suresh Kumar',
                'father_mobile': '9876543214',
                'mother_mobile': '9876543215',
                'course': 'ICSE Class 8',
                'total_fees': 40000,
                'fees_remaining': 0,
            },
            {
                'registration_no': 1004,
                'first_name': 'Ananya',
                'last_name': 'Singh',
                'gender': 'F',
                'father_name': 'Vikram Singh',
                'father_mobile': '9876543216',
                'mother_mobile': '9876543217',
                'course': 'ICSE Class 10',
                'total_fees': 50000,
                'fees_remaining': 25000,
            },
            {
                'registration_no': 1005,
                'first_name': 'Karan',
                'last_name': 'Mehta',
                'gender': 'M',
                'father_name': 'Rohit Mehta',
                'father_mobile': '9876543218',
                'mother_mobile': '9876543219',
                'course': 'ICSE Class 7',
                'total_fees': 35000,
                'fees_remaining': 10000,
            },
        ]
        
        branches = list(Branch.objects.all())
        
        for student_data in students_data:
            # Check if student already exists
            if Student.objects.filter(registration_no=student_data['registration_no']).exists():
                continue
                
            # Create student
            student = Student.objects.create(
                registration_no=student_data['registration_no'],
                date_of_admission=date.today() - timedelta(days=random.randint(30, 365)),
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                gender=student_data['gender'],
                date_of_birth=date.today() - timedelta(days=random.randint(4000, 6000)),
                address=f"Sample Address for {student_data['first_name']} {student_data['last_name']}"
            )
            
            # Create parent info
            ParentInfo.objects.create(
                registration_no=student,
                father_name=student_data['father_name'],
                father_occupation=random.choice(['Engineer', 'Doctor', 'Teacher', 'Businessman', 'Lawyer']),
                father_mobile=student_data['father_mobile'],
                mother_mobile=student_data['mother_mobile'],
            )
            
            # Create academic info
            AcademicInfo.objects.create(
                registration_no=student,
                enrolled_course=student_data['course'],
                branch_code=random.choice(branches),
                percentage_previous_exam=random.uniform(70, 95),
                school_name=f"Sample School {random.randint(1, 10)}"
            )
            
            # Create fee details
            total_fees = student_data['total_fees']
            fees_remaining = student_data['fees_remaining']
            installments = random.randint(2, 4)
            
            FeeDetails.objects.create(
                registration_no=student,
                total_fees=total_fees,
                number_of_installments=installments,
                fees_per_installment=total_fees / installments,
                fees_remaining=fees_remaining
            )
            
            self.stdout.write(f'Created student: {student.full_name} ({student.registration_no})')
        
        self.stdout.write(self.style.SUCCESS('Sample data population completed!'))
        self.stdout.write(self.style.WARNING('Login credentials:'))
        self.stdout.write(self.style.WARNING('Username: admin'))
        self.stdout.write(self.style.WARNING('Password: admin123'))
