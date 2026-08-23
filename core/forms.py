from django import forms
from django.utils import timezone
from .models import Student, ParentInfo, Branch, AcademicInfo, FeeDetails


# Canonical course list — keep registration.html options in sync with these values.
ENROLLED_COURSE_CHOICES = [
    ('', 'Select Course'),
    ('10th ICSE', '10th ICSE'),
    ('9th ICSE', '9th ICSE'),
    ('8th ICSE', '8th ICSE'),
    ('ICSE Class 10', 'ICSE Class 10'),
    ('ICSE Class 9', 'ICSE Class 9'),
    ('ICSE Class 8', 'ICSE Class 8'),
    ('ICSE Class 7', 'ICSE Class 7'),
    ('ICSE Class 6', 'ICSE Class 6'),
    ('Foundation Course', 'Foundation Course'),
]


class StudentRegistrationForm(forms.ModelForm):
    """Form for student registration"""
    
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'date_of_admission': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-neural'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-neural'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter first name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter middle name (optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter last name'}),
            'gender': forms.Select(attrs={'class': 'form-control form-control-neural'}),
            'address': forms.Textarea(attrs={'class': 'form-control form-control-neural', 'rows': 3, 'placeholder': 'Enter complete address'}),
            'registration_no': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter registration number'}),
        }


class ParentInfoForm(forms.ModelForm):
    """Form for parent information"""
    
    class Meta:
        model = ParentInfo
        exclude = ['registration_no']
        widgets = {
            'father_name': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter father\'s name'}),
            'father_occupation': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter father\'s occupation'}),
            'father_mobile': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter father\'s mobile number'}),
            'mother_mobile': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter mother\'s mobile number'}),
        }


class AcademicInfoForm(forms.ModelForm):
    """Form for academic information"""

    enrolled_course = forms.ChoiceField(
        choices=ENROLLED_COURSE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control form-control-neural'}),
        required=True
    )

    class Meta:
        model = AcademicInfo
        exclude = ['registration_no']
        widgets = {
            'branch_code': forms.Select(attrs={'class': 'form-control form-control-neural'}),
            'percentage_previous_exam': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter percentage (0-100)', 'step': '0.01', 'min': '0', 'max': '100'}),
            'school_name': forms.TextInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter current/previous school name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(ENROLLED_COURSE_CHOICES)
        existing_values = {value for value, _ in choices if value}
        # Preserve legacy/custom course values already stored in the database.
        if self.instance and self.instance.pk and self.instance.enrolled_course:
            current = self.instance.enrolled_course
            if current not in existing_values:
                choices.append((current, current))
        self.fields['enrolled_course'].choices = choices


class FeeDetailsForm(forms.ModelForm):
    """Form for fee details"""
    
    class Meta:
        model = FeeDetails
        exclude = ['registration_no']
        widgets = {
            'total_fees': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter total fees amount', 'step': '0.01', 'min': '0.01'}),
            'number_of_installments': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'min': '1', 'max': '12', 'value': '1'}),
            'fees_per_installment': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'readonly': True, 'step': '0.01', 'min': '0'}),
            'fees_remaining': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter remaining fees amount', 'step': '0.01', 'min': '0'}),
            'first_installment': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter first installment amount', 'step': '0.01', 'min': '0.01'}),
            'second_installment': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter second installment amount', 'step': '0.01', 'min': '0.01'}),
            'third_installment': forms.NumberInput(attrs={'class': 'form-control form-control-neural', 'placeholder': 'Enter third installment amount', 'step': '0.01', 'min': '0.01'}),
            'first_installment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-neural', 'min': '2024-01-01', 'max': '2034-12-31'}),
            'second_installment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-neural', 'min': '2024-01-01', 'max': '2034-12-31'}),
            'third_installment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-neural', 'min': '2024-01-01', 'max': '2034-12-31'}),
        }
    
    def clean_total_fees(self):
        total_fees = self.cleaned_data.get('total_fees')
        if total_fees and total_fees <= 0:
            raise forms.ValidationError('Total fees must be positive')
        if total_fees and total_fees > 1000000:  # 10 lakh max
            raise forms.ValidationError('Total fees cannot exceed ₹10,00,000')
        return total_fees
    
    def clean_fees_remaining(self):
        fees_remaining = self.cleaned_data.get('fees_remaining')
        total_fees = self.cleaned_data.get('total_fees')

        if fees_remaining is not None and fees_remaining < 0:
            raise forms.ValidationError('Remaining fees cannot be negative')

        if total_fees is not None and fees_remaining is not None and fees_remaining > total_fees:
            raise forms.ValidationError('Remaining fees cannot exceed total fees')

        return fees_remaining
    
    def clean_first_installment(self):
        amount = self.cleaned_data.get('first_installment')
        total_fees = self.cleaned_data.get('total_fees')
        
        if amount and amount <= 0:
            raise forms.ValidationError('Installment amount must be positive')
        
        if amount and total_fees and amount > total_fees:
            raise forms.ValidationError('Installment amount cannot exceed total fees')
        
        return amount
    
    def clean_second_installment(self):
        amount = self.cleaned_data.get('second_installment')
        total_fees = self.cleaned_data.get('total_fees')
        
        if amount and amount <= 0:
            raise forms.ValidationError('Installment amount must be positive')
        
        if amount and total_fees and amount > total_fees:
            raise forms.ValidationError('Installment amount cannot exceed total fees')
        
        return amount
    
    def clean_third_installment(self):
        amount = self.cleaned_data.get('third_installment')
        total_fees = self.cleaned_data.get('total_fees')
        
        if amount and amount <= 0:
            raise forms.ValidationError('Installment amount must be positive')
        
        if amount and total_fees and amount > total_fees:
            raise forms.ValidationError('Installment amount cannot exceed total fees')
        
        return amount


class FeePaymentForm(forms.Form):
    """Form for recording fee payments"""
    payment_amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-neural',
            'placeholder': 'Enter payment amount',
            'step': '0.01',
            'min': '0.01'
        }),
        label='Payment Amount'
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control form-control-neural'
        }),
        label='Payment Date',
        initial=timezone.now().date()
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('upi', 'UPI'),
            ('bank_transfer', 'Bank Transfer'),
            ('cheque', 'Cheque'),
            ('other', 'Other')
        ],
        widget=forms.Select(attrs={'class': 'form-control form-control-neural'}),
        label='Payment Method'
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-neural',
            'rows': 3,
            'placeholder': 'Enter any remarks (optional)'
        }),
        label='Remarks'
    )