from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.student_registration, name='student_registration'),
    path('students/', views.students_list, name='students_list'),
    path('students/<int:registration_no>/', views.student_detail, name='student_detail'),
    path('students/<int:registration_no>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:registration_no>/payment/', views.fee_payment, name='fee_payment'),
    path('fees/', views.fee_details, name='fee_details'),
    path('whatsapp/', views.whatsapp_panel, name='whatsapp_panel'),
    path('reports/', views.reports, name='reports'),
    
    # Analytics and Reports
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('reports/fees-pdf/', views.generate_fees_report_pdf, name='generate_fees_report_pdf'),
    path('reports/analytics-pdf/', views.generate_analytics_pdf, name='generate_analytics_pdf'),
    path('reports/export-excel/', views.export_data_excel, name='export_data_excel'),
    
    # New panels
    path('blacklisted/', views.blacklisted_students, name='blacklisted_students'),
    path('blacklisted-new/', views.blacklisted_students_new, name='blacklisted_students_new'),
    path('custom-whatsapp/', views.custom_whatsapp_panel, name='custom_whatsapp_panel'),
    path('installments/', views.installment_management, name='installment_management'),
    
    # API endpoints
    path('api/send-whatsapp/', views.send_whatsapp, name='send_whatsapp'),
    path('api/recent-messages/', views.recent_messages, name='recent_messages'),
    path('api/quick-fee-update/', views.quick_fee_update, name='quick_fee_update'),
    path('api/remove-student/', views.remove_student, name='remove_student'),
    path('api/send-bulk-whatsapp/', views.send_bulk_whatsapp, name='send_bulk_whatsapp'),
    path('api/manual-whatsapp-reminders/', views.manual_whatsapp_reminders, name='manual_whatsapp_reminders'),
    path('api/mark-as-paid/', views.mark_as_paid, name='mark_as_paid'),
    path('api/send-custom-whatsapp/', views.send_custom_whatsapp, name='send_custom_whatsapp'),
    path('api/mark-installment-paid/', views.mark_installment_paid, name='mark_installment_paid'),
    path('api/create-installment-records/', views.create_installment_records, name='create_installment_records'),
    path('api/create-installments/', views.create_installments_from_fee_details, name='create_installments_from_fee_details'),
    path('api/update-overdue-statuses/', views.update_overdue_statuses, name='update_overdue_statuses'),
    path('api/run-installment-reminders/', views.run_installment_reminders, name='run_installment_reminders'),
    path('api/send-student-whatsapp/<int:registration_no>/', views.send_student_whatsapp, name='send_student_whatsapp'),
    path('api/generate-receipt/<int:registration_no>/', views.generate_receipt, name='generate_receipt'),
    
    # WhatsApp Message Center
    path('whatsapp-message-center/', views.whatsapp_message_center, name='whatsapp_message_center'),
    path('api/send-individual-whatsapp/', views.send_individual_whatsapp, name='send_individual_whatsapp'),
    path('api/send-bulk-whatsapp-messages/', views.send_bulk_whatsapp_messages, name='send_bulk_whatsapp_messages'),
]