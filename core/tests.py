from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from unittest.mock import patch
import json
from decimal import Decimal

from core.models import ParentInfo, Student, AcademicInfo, Branch, FeeDetails, FeeInstallments
from core.forms import AcademicInfoForm, FeeDetailsForm


class ParentInfoModelTests(TestCase):
    def test_parent_info_fields_after_cleanup(self):
        """ParentInfo should retain father fields and mother_mobile only."""
        field_names = {field.name for field in ParentInfo._meta.get_fields() if hasattr(field, 'column')}
        self.assertIn('father_name', field_names)
        self.assertIn('father_occupation', field_names)
        self.assertIn('father_mobile', field_names)
        self.assertIn('mother_mobile', field_names)
        self.assertNotIn('mother_name', field_names)
        self.assertNotIn('mother_occupation', field_names)

    def test_create_parent_info_without_removed_fields(self):
        student = Student.objects.create(
            registration_no=90001,
            date_of_admission='2024-01-01',
            first_name='Test',
            last_name='Student',
            gender='M',
            date_of_birth='2010-01-01',
        )
        parent = ParentInfo.objects.create(
            registration_no=student,
            father_name='Test Father',
            father_occupation='Engineer',
            father_mobile='9876543210',
            mother_mobile='9876543211',
        )
        self.assertEqual(parent.father_name, 'Test Father')
        self.assertEqual(parent.mother_mobile, '9876543211')


class AcademicInfoFormTests(TestCase):
    def test_legacy_course_value_is_valid_on_edit(self):
        branch = Branch.objects.create(branch_code='TST', branch_name='Test Branch')
        student = Student.objects.create(
            registration_no=90002,
            date_of_admission='2024-01-01',
            first_name='Legacy',
            last_name='Student',
            gender='M',
            date_of_birth='2010-01-01',
        )
        academic = AcademicInfo.objects.create(
            registration_no=student,
            enrolled_course='10th ICSE',
            branch_code=branch,
        )
        form = AcademicInfoForm(instance=academic, data={
            'enrolled_course': '10th ICSE',
            'branch_code': branch.branch_code,
            'percentage_previous_exam': '90',
            'school_name': 'Test School',
        })
        self.assertTrue(form.is_valid(), form.errors)


class StudentEditFeeSaveTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(branch_code='KATOL', branch_name='Katol Branch')
        self.student = Student.objects.create(
            registration_no=21001,
            date_of_admission='2026-02-02',
            first_name='Aditri',
            middle_name='Rajiv',
            last_name='Verma',
            gender='F',
            date_of_birth='2011-12-31',
            address='Koradi Road',
        )
        ParentInfo.objects.create(
            registration_no=self.student,
            father_name='Rajiv Verma',
            father_occupation='Business',
            father_mobile='9422113207',
            mother_mobile='9423687169',
        )
        AcademicInfo.objects.create(
            registration_no=self.student,
            enrolled_course='10th ICSE',
            branch_code=self.branch,
            percentage_previous_exam='90.00',
            school_name='CDS',
        )
        self.fee_details = FeeDetails.objects.create(
            registration_no=self.student,
            total_fees='20000.00',
            number_of_installments=2,
            fees_per_installment='10000.00',
            fees_remaining='2.00',
        )
        self.user = User.objects.create_user(username='testadmin', password='testpass')

    def test_student_edit_saves_fees_remaining_when_legacy_course_present(self):
        post_data = {
            'registration_no': '21001',
            'date_of_admission': '2026-02-02',
            'first_name': 'Aditri',
            'middle_name': 'Rajiv',
            'last_name': 'Verma',
            'gender': 'F',
            'date_of_birth': '2011-12-31',
            'address': 'Koradi Road',
            'father_name': 'Rajiv Verma',
            'father_occupation': 'Business',
            'father_mobile': '9422113207',
            'mother_mobile': '9423687169',
            'enrolled_course': '10th ICSE',
            'branch_code': 'KATOL',
            'percentage_previous_exam': '90.00',
            'school_name': 'CDS',
            'total_fees': '20000.00',
            'number_of_installments': '2',
            'fees_per_installment': '10000.00',
            'fees_remaining': '20000.00',
            'first_installment': '10000',
            'first_installment_date': '2025-01-01',
            'second_installment': '10000',
            'second_installment_date': '2025-06-01',
        }

        with override_settings(ALLOWED_HOSTS=['testserver', 'localhost']):
            client = Client()
            client.login(username='testadmin', password='testpass')
            response = client.post('/students/21001/edit/', post_data)

        self.assertEqual(response.status_code, 302)
        self.fee_details.refresh_from_db()
        self.assertEqual(str(self.fee_details.fees_remaining), '20000.00')


class SingleInstallmentTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(branch_code='SADAR', branch_name='Sadar Branch')
        self.user = User.objects.create_user(username='testadmin', password='testpass')

    def test_registration_creates_single_installment_with_due_date(self):
        post_data = {
            'registration_no': '31001',
            'date_of_admission': '2026-06-01',
            'first_name': 'Single',
            'last_name': 'Installment',
            'gender': 'M',
            'date_of_birth': '2010-01-01',
            'father_name': 'Test Father',
            'father_mobile': '9876543210',
            'enrolled_course': '10th ICSE',
            'branch_code': 'SADAR',
            'total_fees': '30000.00',
            'number_of_installments': '1',
            'fees_per_installment': '30000.00',
            'fees_remaining': '30000.00',
            'first_installment': '30000',
            'first_installment_date': '2026-07-01',
        }

        with override_settings(ALLOWED_HOSTS=['testserver', 'localhost']), patch('builtins.print'):
            client = Client()
            client.login(username='testadmin', password='testpass')
            response = client.post('/register/', post_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        installments = FeeInstallments.objects.filter(registration_no=31001)
        self.assertEqual(installments.count(), 1)
        installment = installments.get()
        self.assertEqual(installment.installment_no, 1)
        self.assertEqual(str(installment.amount), '30000.00')
        self.assertEqual(str(installment.due_date), '2026-07-01')

    def test_student_edit_creates_single_installment_with_due_date(self):
        student = Student.objects.create(
            registration_no=31002,
            date_of_admission='2026-06-01',
            first_name='Edit',
            last_name='Student',
            gender='M',
            date_of_birth='2010-01-01',
        )
        ParentInfo.objects.create(
            registration_no=student,
            father_name='Test Father',
            father_mobile='9876543210',
        )
        AcademicInfo.objects.create(
            registration_no=student,
            enrolled_course='10th ICSE',
            branch_code=self.branch,
        )
        FeeDetails.objects.create(
            registration_no=student,
            total_fees='15000.00',
            number_of_installments=1,
            fees_per_installment='15000.00',
            fees_remaining='15000.00',
        )

        post_data = {
            'registration_no': '31002',
            'date_of_admission': '2026-06-01',
            'first_name': 'Edit',
            'last_name': 'Student',
            'gender': 'M',
            'date_of_birth': '2010-01-01',
            'father_name': 'Test Father',
            'father_mobile': '9876543210',
            'enrolled_course': '10th ICSE',
            'branch_code': 'SADAR',
            'total_fees': '15000.00',
            'number_of_installments': '1',
            'fees_per_installment': '15000.00',
            'fees_remaining': '15000.00',
            'first_installment': '15000',
            'first_installment_date': '2026-08-15',
        }

        with override_settings(ALLOWED_HOSTS=['testserver', 'localhost']):
            client = Client()
            client.login(username='testadmin', password='testpass')
            response = client.post('/students/31002/edit/', post_data)

        self.assertEqual(response.status_code, 302)
        installments = FeeInstallments.objects.filter(registration_no=student)
        self.assertEqual(installments.count(), 1)
        installment = installments.get()
        self.assertEqual(installment.installment_no, 1)
        self.assertEqual(str(installment.amount), '15000.00')
        self.assertEqual(str(installment.due_date), '2026-08-15')


class WhatsAppServiceTests(TestCase):
    def _create_student_with_contacts(self, registration_no, father_mobile='', mother_mobile=''):
        student = Student.objects.create(
            registration_no=registration_no,
            date_of_admission='2026-01-01',
            first_name=f'Student{registration_no}',
            last_name='WhatsApp',
            gender='M',
            date_of_birth='2010-01-01',
        )
        ParentInfo.objects.create(
            registration_no=student,
            father_name='Test Father',
            father_mobile=father_mobile,
            mother_mobile=mother_mobile,
        )
        return student

    def test_format_phone_number_valid_10_digit(self):
        from core.whatsapp_service import format_phone_number

        self.assertEqual(format_phone_number('9822574252'), '+919822574252')
        self.assertEqual(format_phone_number('9527722785'), '+919527722785')

    def test_format_phone_number_with_country_code(self):
        from core.whatsapp_service import format_phone_number

        self.assertEqual(format_phone_number('+919822574252'), '+919822574252')
        self.assertEqual(format_phone_number('919822574252'), '+919822574252')

    def test_format_phone_number_invalid(self):
        from core.whatsapp_service import format_phone_number

        self.assertIsNone(format_phone_number('12345'))
        self.assertIsNone(format_phone_number(''))

    def test_send_returns_failure_for_invalid_number(self):
        from core.whatsapp_service import send_whatsapp_message

        result = send_whatsapp_message('invalid', 'test message')
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)

    def test_selenium_availability_check(self):
        from core.whatsapp_service import is_selenium_available

        available, error = is_selenium_available()
        # In test environment, selenium might not be installed, but the function should not crash
        self.assertIsInstance(available, bool)
        if not available:
            self.assertIsNotNone(error)

    def test_student_contact_send_sends_to_father_and_mother(self):
        from core.whatsapp_service import WhatsAppSendResult, send_whatsapp_to_student_contacts

        student = self._create_student_with_contacts(91001, '9822574252', '9527722785')
        calls = []

        def fake_send(phone_number, message):
            calls.append(phone_number)
            return WhatsAppSendResult(success=True, phone_number=phone_number)

        result = send_whatsapp_to_student_contacts(
            student,
            'test message',
            message_type='birthday',
            send_func=fake_send,
        )

        self.assertTrue(result.success)
        self.assertEqual(calls, ['+919822574252', '+919527722785'])
        self.assertEqual(result.successful_numbers, ['+919822574252', '+919527722785'])
        self.assertEqual(result.failed_numbers, [])
        self.assertEqual(result.status, 'sent')

    def test_father_failure_does_not_stop_mother_delivery(self):
        from core.whatsapp_service import WhatsAppSendResult, send_whatsapp_to_student_contacts

        student = self._create_student_with_contacts(91002, '9822574252', '9527722785')
        calls = []

        def fake_send(phone_number, message):
            calls.append(phone_number)
            return WhatsAppSendResult(
                success=phone_number == '+919527722785',
                phone_number=phone_number,
                error=None if phone_number == '+919527722785' else 'Father failed',
            )

        result = send_whatsapp_to_student_contacts(
            student,
            'test message',
            message_type='reminder_1',
            send_func=fake_send,
        )

        self.assertTrue(result.success)
        self.assertEqual(calls, ['+919822574252', '+919527722785'])
        self.assertEqual(result.successful_numbers, ['+919527722785'])
        self.assertEqual(result.failed_numbers, ['+919822574252'])
        self.assertEqual(result.status, 'sent')

    def test_mother_failure_does_not_undo_father_delivery(self):
        from core.whatsapp_service import WhatsAppSendResult, send_whatsapp_to_student_contacts

        student = self._create_student_with_contacts(91003, '9822574252', '9527722785')
        calls = []

        def fake_send(phone_number, message):
            calls.append(phone_number)
            return WhatsAppSendResult(
                success=phone_number == '+919822574252',
                phone_number=phone_number,
                error=None if phone_number == '+919822574252' else 'Mother failed',
            )

        result = send_whatsapp_to_student_contacts(
            student,
            'test message',
            message_type='reminder_2',
            send_func=fake_send,
        )

        self.assertTrue(result.success)
        self.assertEqual(calls, ['+919822574252', '+919527722785'])
        self.assertEqual(result.successful_numbers, ['+919822574252'])
        self.assertEqual(result.failed_numbers, ['+919527722785'])
        self.assertEqual(result.status, 'sent')

    def test_student_contact_send_fails_only_after_both_numbers_fail(self):
        from core.whatsapp_service import WhatsAppSendResult, send_whatsapp_to_student_contacts

        student = self._create_student_with_contacts(91007, '9822574252', '9527722785')

        def fake_send(phone_number, message):
            return WhatsAppSendResult(success=False, phone_number=phone_number, error='Timeout')

        result = send_whatsapp_to_student_contacts(
            student,
            'test message',
            message_type='reminder_2',
            send_func=fake_send,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.attempted_numbers, ['+919822574252', '+919527722785'])
        self.assertEqual(result.successful_numbers, [])
        self.assertEqual(result.failed_numbers, ['+919822574252', '+919527722785'])
        self.assertEqual(result.status, 'failed')
        self.assertIn('Timeout', result.failure_reason)

    def test_duplicate_numbers_are_sent_only_once(self):
        from core.whatsapp_service import WhatsAppSendResult, send_whatsapp_to_student_contacts

        student = self._create_student_with_contacts(91004, '9822574252', '+919822574252')
        calls = []

        result = send_whatsapp_to_student_contacts(
            student,
            'test message',
            message_type='birthday',
            send_func=lambda phone, message: calls.append(phone) or WhatsAppSendResult(success=True, phone_number=phone),
        )

        self.assertTrue(result.success)
        self.assertEqual(calls, ['+919822574252'])
        self.assertEqual(result.successful_numbers, ['+919822574252'])

    def test_invalid_numbers_are_removed_before_send(self):
        from core.whatsapp_service import send_whatsapp_to_student_contacts

        student = self._create_student_with_contacts(91008, 'invalid', '')
        calls = []

        result = send_whatsapp_to_student_contacts(
            student,
            'test message',
            message_type='birthday',
            send_func=lambda phone, message: calls.append(phone),
        )

        self.assertFalse(result.success)
        self.assertEqual(calls, [])
        self.assertEqual(result.attempted_numbers, [])
        self.assertEqual(result.failure_reason, 'No valid WhatsApp contact numbers found')

    def test_clean_whatsapp_message_removes_unicode_surrogates(self):
        from core.whatsapp_service import clean_whatsapp_message

        text = "Test message with bad chars \ud83e\udd14 and valid text"
        result = clean_whatsapp_message(text)
        self.assertNotIn('\ud83e', result)
        self.assertIn('Test message', result)

    def test_clean_whatsapp_message_converts_crlf_to_lf(self):
        from core.whatsapp_service import clean_whatsapp_message

        text = "Line1\r\nLine2\r\nLine3"
        result = clean_whatsapp_message(text)
        self.assertNotIn('\r\n', result)
        self.assertIn('Line1\nLine2\nLine3', result)

    def test_clean_whatsapp_message_removes_extra_blank_lines(self):
        from core.whatsapp_service import clean_whatsapp_message

        text = "Line1\n\n\n\n\nLine2"
        result = clean_whatsapp_message(text)
        self.assertEqual(result, "Line1\n\nLine2")

    def test_clean_whatsapp_message_strips_whitespace(self):
        from core.whatsapp_service import clean_whatsapp_message

        text = "  Hello World  \n"
        result = clean_whatsapp_message(text)
        self.assertEqual(result, "Hello World")

    def test_clean_whatsapp_message_converts_list_to_string(self):
        from core.whatsapp_service import clean_whatsapp_message

        result = clean_whatsapp_message(['9822574252', '9970165331'])
        self.assertEqual(result, "9822574252, 9970165331")

    def test_clean_whatsapp_message_converts_dict_to_string(self):
        from core.whatsapp_service import clean_whatsapp_message

        result = clean_whatsapp_message({'father': '9822574252'})
        self.assertIn('father', result)
        self.assertIn('9822574252', result)

    def test_clean_whatsapp_message_removes_control_chars(self):
        from core.whatsapp_service import clean_whatsapp_message

        text = "Hello\x00World\x1fTest"
        result = clean_whatsapp_message(text)
        self.assertEqual(result, "HelloWorldTest")

    def test_send_admin_summary_wrapped_in_try_except(self):
        from core.whatsapp_service import send_admin_summary
        # Should not raise any exception - uses send_whatsapp_message under the hood
        # which will fail gracefully since we don't have selenium fully configured in test
        result = send_admin_summary("Test summary message")
        # Without selenium configured, it returns a failure result, not an exception
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)

    def test_one_student_failure_does_not_stop_remaining_students(self):
        from core.whatsapp_service import WhatsAppSendResult, send_whatsapp_to_student_contacts

        failing_student = self._create_student_with_contacts(91005, '9822574252', '9527722785')
        succeeding_student = self._create_student_with_contacts(91006, '9527722785', '')
        processed = []

        def fake_send(phone_number, message):
            processed.append(phone_number)
            if phone_number in ['+919822574252', '+919527722785'] and len(processed) <= 2:
                raise RuntimeError('Browser automation failed')
            return WhatsAppSendResult(success=True, phone_number=phone_number)

        results = []
        for student in [failing_student, succeeding_student]:
            try:
                results.append(send_whatsapp_to_student_contacts(
                    student,
                    'test message',
                    message_type='birthday',
                    send_func=fake_send,
                ))
            except Exception:
                continue

        self.assertEqual(len(results), 2)
        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)
        self.assertEqual(processed, ['+919822574252', '+919527722785', '+919527722785'])




class FeeCalculationTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(branch_code='FEE', branch_name='Fee Branch')
        self.student = Student.objects.create(
            registration_no=40001,
            date_of_admission='2026-01-01',
            first_name='Fee',
            last_name='Test',
            gender='M',
            date_of_birth='2010-01-01',
        )
        self.fee_details = FeeDetails.objects.create(
            registration_no=self.student,
            total_fees='25000.00',
            number_of_installments=3,
            fees_per_installment='10000.00',
            fees_remaining='25000.00',
        )

    def test_installment_summary_sums_amounts_not_multiplies(self):
        from core.fee_utils import get_installment_summary

        FeeInstallments.objects.create(
            registration_no=self.student, installment_no=1, amount='10000.00',
            due_date='2026-02-01', status='Due'
        )
        FeeInstallments.objects.create(
            registration_no=self.student, installment_no=2, amount='10000.00',
            due_date='2026-03-01', status='Due'
        )
        FeeInstallments.objects.create(
            registration_no=self.student, installment_no=3, amount='5000.00',
            due_date='2026-04-01', status='Due'
        )

        summary = get_installment_summary(
            FeeInstallments.objects.filter(registration_no=self.student)
        )
        self.assertEqual(summary['total_count'], 3)
        self.assertEqual(str(summary['total_amount']), '25000.00')

    def test_split_amount_evenly_handles_decimal_remainder(self):
        from core.fee_utils import split_amount_evenly

        amounts = split_amount_evenly('25000', 3)
        self.assertEqual([str(a) for a in amounts], ['8333.33', '8333.33', '8333.34'])
        self.assertEqual(sum(amounts), Decimal('25000.00'))

    def test_mark_installment_paid_syncs_dashboard_fees(self):
        from decimal import Decimal

        inst1 = FeeInstallments.objects.create(
            registration_no=self.student, installment_no=1, amount='10000.00',
            due_date='2026-02-01', status='Due'
        )
        FeeInstallments.objects.create(
            registration_no=self.student, installment_no=2, amount='10000.00',
            due_date='2026-03-01', status='Due'
        )
        FeeInstallments.objects.create(
            registration_no=self.student, installment_no=3, amount='5000.00',
            due_date='2026-04-01', status='Due'
        )

        inst1.mark_as_paid()
        self.fee_details.refresh_from_db()

        self.assertEqual(self.fee_details.fees_paid, Decimal('10000.00'))
        self.assertEqual(self.fee_details.fees_remaining, Decimal('15000.00'))

    def test_mark_installment_paid_api_updates_fees(self):
        from django.contrib.auth.models import User

        user = User.objects.create_user(username='feeadmin', password='testpass')
        inst = FeeInstallments.objects.create(
            registration_no=self.student, installment_no=1, amount='10000.00',
            due_date='2026-02-01', status='Due'
        )
        FeeInstallments.objects.create(
            registration_no=self.student, installment_no=2, amount='15000.00',
            due_date='2026-03-01', status='Due'
        )

        with override_settings(ALLOWED_HOSTS=['testserver', 'localhost']):
            client = Client()
            client.login(username='feeadmin', password='testpass')
            response = client.post(
                '/api/mark-installment-paid/',
                data=json.dumps({'installment_id': inst.installment_id}),
                content_type='application/json',
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['fees_paid'], 10000.0)
        self.assertEqual(data['fees_remaining'], 15000.0)

        self.fee_details.refresh_from_db()
        self.assertEqual(str(self.fee_details.fees_remaining), '15000.00')
