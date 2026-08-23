from django.contrib import admin
from .models import Student, ParentInfo, Branch, AcademicInfo, FeeDetails, CustomMessageLog, FeeInstallments


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['branch_code', 'branch_name', 'branch_location']
    search_fields = ['branch_name', 'branch_code']


class ParentInfoInline(admin.TabularInline):
    model = ParentInfo
    extra = 0


class AcademicInfoInline(admin.TabularInline):
    model = AcademicInfo
    extra = 0


class FeeDetailsInline(admin.TabularInline):
    model = FeeDetails
    extra = 0


class FeeInstallmentsInline(admin.TabularInline):
    model = FeeInstallments
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['registration_no', 'full_name', 'gender', 'date_of_admission', 'get_course', 'get_fees_status']
    list_filter = ['gender', 'date_of_admission']
    search_fields = ['first_name', 'last_name', 'registration_no']
    inlines = [ParentInfoInline, AcademicInfoInline, FeeDetailsInline, FeeInstallmentsInline]
    
    def get_course(self, obj):
        try:
            return obj.academicinfo.enrolled_course
        except:
            return 'N/A'
    get_course.short_description = 'Course'
    
    def get_fees_status(self, obj):
        try:
            if obj.feeDetails.fees_remaining > 0:
                return f'₹{obj.feeDetails.fees_remaining} Pending'
            else:
                return 'Paid'
        except:
            return 'N/A'
    get_fees_status.short_description = 'Fee Status'


@admin.register(ParentInfo)
class ParentInfoAdmin(admin.ModelAdmin):
    list_display = ['registration_no', 'father_name', 'mother_name', 'father_mobile', 'mother_mobile']
    search_fields = ['father_name', 'mother_name', 'father_mobile', 'mother_mobile']


@admin.register(AcademicInfo)
class AcademicInfoAdmin(admin.ModelAdmin):
    list_display = ['registration_no', 'enrolled_course', 'branch_code', 'percentage_previous_exam']
    list_filter = ['enrolled_course', 'branch_code']
    search_fields = ['registration_no__first_name', 'registration_no__last_name']


@admin.register(FeeDetails)
class FeeDetailsAdmin(admin.ModelAdmin):
    list_display = ['registration_no', 'total_fees', 'fees_paid', 'fees_remaining', 'number_of_installments']
    list_filter = ['number_of_installments']
    search_fields = ['registration_no__first_name', 'registration_no__last_name']
    
    def fees_paid(self, obj):
        return obj.fees_paid
    fees_paid.short_description = 'Fees Paid'


@admin.register(CustomMessageLog)
class CustomMessageLogAdmin(admin.ModelAdmin):
    list_display = ['student', 'message_text_preview', 'sent_status', 'timestamp', 'has_attachment']
    list_filter = ['sent_status', 'timestamp']
    search_fields = ['student__first_name', 'student__last_name', 'message_text']
    readonly_fields = ['timestamp']
    
    def message_text_preview(self, obj):
        return obj.message_text[:50] + '...' if len(obj.message_text) > 50 else obj.message_text
    message_text_preview.short_description = 'Message Preview'
    
    def has_attachment(self, obj):
        return bool(obj.attachment)
    has_attachment.boolean = True
    has_attachment.short_description = 'Has Attachment'


@admin.register(FeeInstallments)
class FeeInstallmentsAdmin(admin.ModelAdmin):
    list_display = ['registration_no', 'installment_no', 'amount', 'due_date', 'status', 'paid_date', 'days_overdue']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['registration_no__first_name', 'registration_no__last_name', 'registration_no__registration_no']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_paid', 'update_overdue_status']
    
    def days_overdue(self, obj):
        return obj.days_overdue
    days_overdue.short_description = 'Days Overdue'
    
    def mark_as_paid(self, request, queryset):
        updated = 0
        for installment in queryset:
            if installment.status != 'Paid':
                installment.mark_as_paid()
                updated += 1
        self.message_user(request, f'{updated} installments marked as paid.')
    mark_as_paid.short_description = 'Mark selected installments as paid'
    
    def update_overdue_status(self, request, queryset):
        from datetime import date
        today = date.today()
        updated = queryset.filter(due_date__lt=today, status='Due').update(status='Pending')
        self.message_user(request, f'{updated} installments updated to Pending status.')
    update_overdue_status.short_description = 'Update overdue installments to Pending'
