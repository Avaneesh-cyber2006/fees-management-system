from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date, datetime
from decimal import Decimal


class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    registration_no = models.IntegerField(primary_key=True, db_column='Registration_No', verbose_name="Registration No")
    date_of_admission = models.DateField(db_column='Date_of_Admission', verbose_name="Date of Admission")
    first_name = models.CharField(max_length=50, db_column='First_Name', verbose_name="First Name")
    middle_name = models.CharField(max_length=50, blank=True, null=True, db_column='Middle_Name', verbose_name="Middle Name")
    last_name = models.CharField(max_length=50, db_column='Last_Name', verbose_name="Last Name")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, db_column='Gender', verbose_name="Gender")
    date_of_birth = models.DateField(db_column='Date_of_Birth', verbose_name="Date of Birth")
    address = models.TextField(blank=True, null=True, db_column='Address', verbose_name="Address")
    
    class Meta:
        db_table = 'student'
        verbose_name = "Student"
        verbose_name_plural = "Students"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.registration_no})"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class Branch(models.Model):
    branch_code = models.CharField(max_length=10, primary_key=True, db_column='Branch_Code', verbose_name="Branch Code")
    branch_name = models.CharField(max_length=50, unique=True, db_column='Branch_Name', verbose_name="Branch Name")
    branch_location = models.CharField(max_length=100, blank=True, null=True, db_column='Branch_Location', verbose_name="Branch Location")
    
    class Meta:
        db_table = 'branch'
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
    
    def __str__(self):
        return f"{self.branch_name} ({self.branch_code})"


class ParentInfo(models.Model):
    parent_id = models.AutoField(primary_key=True, db_column='Parent_ID', verbose_name="Parent ID")
    registration_no = models.OneToOneField(Student, on_delete=models.CASCADE, db_column='Registration_No', verbose_name="Student", related_name='parentinfo')
    father_name = models.CharField(max_length=50, db_column='Father_Name', verbose_name="Father's Name")
    father_occupation = models.CharField(max_length=50, blank=True, null=True, db_column='Father_Occupation', verbose_name="Father's Occupation")
    father_mobile = models.CharField(max_length=15, blank=True, null=True, db_column='Father_Mobile', verbose_name="Father's Mobile")
    mother_mobile = models.CharField(max_length=15, blank=True, null=True, db_column='Mother_Mobile', verbose_name="Mother's Mobile")
    
    class Meta:
        db_table = 'parent_info'
        verbose_name = "Parent Information"
        verbose_name_plural = "Parent Information"
    
    def __str__(self):
        return f"Parents of {self.registration_no.full_name}"


class AcademicInfo(models.Model):
    academic_id = models.AutoField(primary_key=True, db_column='Academic_ID', verbose_name="Academic ID")
    registration_no = models.OneToOneField(Student, on_delete=models.CASCADE, db_column='Registration_No', verbose_name="Student", related_name='academicinfo')
    enrolled_course = models.CharField(max_length=50, db_column='Enrolled_Course', verbose_name="Enrolled Course")
    branch_code = models.ForeignKey(Branch, on_delete=models.RESTRICT, db_column='Branch_Code', verbose_name="Branch")
    percentage_previous_exam = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, db_column='Percentage_Previous_Exam', verbose_name="Previous Exam %")
    school_name = models.CharField(max_length=100, blank=True, null=True, db_column='School_Name', verbose_name="School Name")
    
    class Meta:
        db_table = 'academic_info'
        verbose_name = "Academic Information"
        verbose_name_plural = "Academic Information"
    
    def __str__(self):
        return f"{self.registration_no.full_name} - {self.enrolled_course}"


class FeeDetails(models.Model):
    fee_id = models.AutoField(primary_key=True, db_column='Fee_ID', verbose_name="Fee ID")
    registration_no = models.OneToOneField(Student, on_delete=models.CASCADE, db_column='Registration_No', verbose_name="Student", related_name='feedetails')
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Total_Fees', verbose_name="Total Fees")
    number_of_installments = models.IntegerField(default=1, db_column='Number_of_Installments', verbose_name="Number of Installments")
    fees_per_installment = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Fees_Per_Installment', verbose_name="Fees per Installment")
    fees_remaining = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Fees_Remaining', verbose_name="Fees Remaining")
    first_installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='first_installment', verbose_name="First Installment")
    second_installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='second_installment', verbose_name="Second Installment")
    third_installment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='third_installment', verbose_name="Third Installment")
    first_installment_date = models.DateField(blank=True, null=True, db_column='first_installment_date', verbose_name="First Installment Date")
    second_installment_date = models.DateField(blank=True, null=True, db_column='second_installment_date', verbose_name="Second Installment Date")
    third_installment_date = models.DateField(blank=True, null=True, db_column='third_installment_date', verbose_name="Third Installment Date")
    
    class Meta:
        db_table = 'fee_details'
        verbose_name = "Fee Details"
        verbose_name_plural = "Fee Details"
    
    def __str__(self):
        return f"{self.registration_no.full_name} - ₹{self.fees_remaining} remaining"
    
    @property
    def fees_paid(self):
        """Fees paid — derived from paid installments when records exist."""
        from django.db.models import Sum

        installments = self.registration_no.installments.all()
        if installments.exists():
            paid_total = installments.filter(status='Paid').aggregate(
                total=Sum('amount')
            )['total']
            return paid_total or Decimal('0')
        return self.total_fees - self.fees_remaining

    def sync_from_installments(self):
        """
        Recalculate fees_remaining from installment payment status.
        Installment records are the source of truth for payment totals.
        """
        from django.db.models import Sum

        installments = self.registration_no.installments.all()
        if not installments.exists():
            return

        paid_total = installments.filter(status='Paid').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        new_remaining = max(Decimal('0'), self.total_fees - paid_total)

        if self.fees_remaining != new_remaining:
            FeeDetails.objects.filter(pk=self.pk).update(fees_remaining=new_remaining)
            self.fees_remaining = new_remaining
    
    @property
    def is_overdue(self):
        from datetime import date
        # Check if any installment date has passed and fees are still remaining
        if self.fees_remaining <= 0:
            return False
        
        today = date.today()
        installment_dates = [
            self.first_installment_date,
            self.second_installment_date,
            self.third_installment_date
        ]
        
        # Check if any due date has passed
        for due_date in installment_dates:
            if due_date and due_date < today:
                return True
        return False
    
    @property
    def next_due_date(self):
        from datetime import date
        today = date.today()
        installment_dates = [
            self.first_installment_date,
            self.second_installment_date,
            self.third_installment_date
        ]
        
        # Filter out null dates and sort
        valid_dates = [date for date in installment_dates if date is not None]
        if not valid_dates:
            return None
        
        valid_dates.sort()
        
        # Find the next due date (closest to today, including past dates)
        future_dates = [date for date in valid_dates if date >= today]
        if future_dates:
            return future_dates[0]
        
        # If no future dates, return the most recent past date
        return valid_dates[-1]
    
    def clean(self):
        """Validate fee details data"""
        super().clean()
        
        # Validate amounts are positive
        if self.total_fees < 0:
            raise ValidationError({'total_fees': 'Total fees cannot be negative'})
        
        if self.fees_remaining < 0:
            raise ValidationError({'fees_remaining': 'Remaining fees cannot be negative'})
        
        if self.fees_remaining > self.total_fees:
            raise ValidationError({'fees_remaining': 'Remaining fees cannot exceed total fees'})
        
        # Validate installment amounts
        if self.first_installment:
            if self.first_installment <= 0:
                raise ValidationError({'first_installment': 'Installment amount must be positive'})
            if self.first_installment > self.total_fees:
                raise ValidationError({'first_installment': 'Installment amount cannot exceed total fees'})
        
        if self.second_installment:
            if self.second_installment <= 0:
                raise ValidationError({'second_installment': 'Installment amount must be positive'})
            if self.second_installment > self.total_fees:
                raise ValidationError({'second_installment': 'Installment amount cannot exceed total fees'})
        
        if self.third_installment:
            if self.third_installment <= 0:
                raise ValidationError({'third_installment': 'Installment amount must be positive'})
            if self.third_installment > self.total_fees:
                raise ValidationError({'third_installment': 'Installment amount cannot exceed total fees'})
        
        # Validate installment dates are reasonable (not in distant past or future)
        current_year = date.today().year
        valid_year_range = range(current_year - 1, current_year + 10)
        
        if self.first_installment_date:
            if self.first_installment_date.year not in valid_year_range:
                raise ValidationError({'first_installment_date': f'Date must be between {current_year-1} and {current_year+10}'})
        
        if self.second_installment_date:
            if self.second_installment_date.year not in valid_year_range:
                raise ValidationError({'second_installment_date': f'Date must be between {current_year-1} and {current_year+10}'})
        
        if self.third_installment_date:
            if self.third_installment_date.year not in valid_year_range:
                raise ValidationError({'third_installment_date': f'Date must be between {current_year-1} and {current_year+10}'})
        
        # Validate installment dates are in chronological order
        dates = []
        if self.first_installment_date:
            dates.append(('first', self.first_installment_date))
        if self.second_installment_date:
            dates.append(('second', self.second_installment_date))
        if self.third_installment_date:
            dates.append(('third', self.third_installment_date))
        
        if len(dates) > 1:
            dates.sort(key=lambda x: x[1])
            for i in range(1, len(dates)):
                if dates[i][1] <= dates[i-1][1]:
                    raise ValidationError(f'{dates[i][0].title()} installment date must be after {dates[i-1][0]} installment date')
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def days_overdue(self):
        from datetime import date
        next_due = self.next_due_date
        if not next_due:
            return 0
        
        today = date.today()
        days_diff = (today - next_due).days
        return max(0, days_diff)


class FeeInstallments(models.Model):
    STATUS_CHOICES = [
        ('Due', 'Due'),
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]
    
    installment_id = models.AutoField(primary_key=True, db_column='Installment_ID', verbose_name="Installment ID")
    registration_no = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='Registration_No', verbose_name="Student", related_name='installments')
    installment_no = models.IntegerField(db_column='Installment_No', verbose_name="Installment Number")
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='Amount', verbose_name="Amount")
    due_date = models.DateField(db_column='Due_Date', verbose_name="Due Date")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Due', db_column='Status', verbose_name="Status")
    paid_date = models.DateField(blank=True, null=True, db_column='Paid_Date', verbose_name="Paid Date")
    created_at = models.DateTimeField(auto_now_add=True, db_column='Created_At', verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, db_column='Updated_At', verbose_name="Updated At")
    
    class Meta:
        db_table = 'fee_installments'
        verbose_name = "Fee Installment"
        verbose_name_plural = "Fee Installments"
        ordering = ['registration_no', 'installment_no']
        unique_together = ['registration_no', 'installment_no']
    
    def __str__(self):
        return f"{self.registration_no.full_name} - Installment {self.installment_no} (₹{self.amount})"
    
    def clean(self):
        """Validate installment data"""
        super().clean()
        
        # Validate amount is positive
        if self.amount <= 0:
            raise ValidationError({'amount': 'Installment amount must be positive'})
        
        # Validate installment number is positive
        if self.installment_no <= 0:
            raise ValidationError({'installment_no': 'Installment number must be positive'})
        
        # Validate due date is reasonable (not in distant past or future)
        current_year = date.today().year
        valid_year_range = range(current_year - 1, current_year + 10)
        
        if self.due_date.year not in valid_year_range:
            raise ValidationError({'due_date': f'Due date must be between {current_year-1} and {current_year+10}'})
        
        # Validate paid_date is not in future if status is Paid
        if self.status == 'Paid' and self.paid_date:
            if self.paid_date > date.today():
                raise ValidationError({'paid_date': 'Paid date cannot be in the future'})
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        from datetime import date
        return self.due_date < date.today() and self.status != 'Paid'
    
    @property
    def days_overdue(self):
        from datetime import date
        if self.status == 'Paid':
            return 0
        today = date.today()
        if self.due_date < today:
            return (today - self.due_date).days
        return 0
    
    def mark_as_paid(self):
        """Mark installment as paid and sync parent fee totals."""
        from datetime import date

        if self.status == 'Paid':
            return

        self.status = 'Paid'
        self.paid_date = date.today()
        self.save()
    
    @classmethod
    def update_overdue_statuses(cls):
        """Update Due status to Pending for overdue installments"""
        from datetime import date
        today = date.today()
        
        overdue_installments = cls.objects.filter(
            due_date__lt=today,
            status='Due'
        )
        
        updated_count = overdue_installments.update(status='Pending')
        return updated_count


class CustomMessageLog(models.Model):
    message_id = models.AutoField(primary_key=True, db_column='Message_ID', verbose_name="Message ID")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='Student_ID', verbose_name="Student", related_name='custom_messages')
    message_text = models.TextField(db_column='Message_Text', verbose_name="Message Text")
    attachment = models.CharField(max_length=255, blank=True, null=True, db_column='Attachment', verbose_name="Attachment Path")
    timestamp = models.DateTimeField(auto_now_add=True, db_column='Timestamp', verbose_name="Timestamp")
    sent_status = models.CharField(max_length=20, default='PENDING', db_column='Sent_Status', verbose_name="Sent Status")
    
    class Meta:
        db_table = 'custom_message_log'
        verbose_name = "Custom Message Log"
        verbose_name_plural = "Custom Message Logs"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Message to {self.student.full_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"



