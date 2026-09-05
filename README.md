# Fees Management System

A Django-based fees management system for coaching classes with student management, fee tracking, installment management, and WhatsApp reminder automation.

## Features

### Student Management
- Complete student registration with personal information
- Parent information management with contact details
- Academic information including course enrollment and branch details
- Student directory with search and filter functionality
- Detailed student profiles with complete information

### Fee Management
- Fee structure management with total fees and installment plans
- Installment tracking with unlimited installment support
- Due date management and overdue tracking
- Payment recording and fee status monitoring
- Dynamic installment management with auto-fill functionality

### WhatsApp Automation
- Selenium-based WhatsApp Web automation for sending reminders
- Automated fee reminders based on installment due dates
- Birthday message automation for students
- Custom message templates for different scenarios
- Multiple parent contact support (father and mother)
- Message logging and tracking
- Admin notification system for sent messages

### Dashboard & Reports
- Real-time statistics dashboard
- Student count and fee collection analytics
- Installment status overview
- Recent activities tracking
- PDF report generation capabilities

## Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL with custom schema
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **WhatsApp Automation**: Selenium WebDriver
- **PDF Generation**: ReportLab, xhtml2pdf
- **Data Processing**: Pandas, openpyxl
- **Charts**: Matplotlib, Plotly

## Project Structure

```
fees_management_system/
├── core/                              # Main Django app
│   ├── management/commands/           # Custom Django management commands
│   │   ├── populate_sample_data.py    # Sample data population
│   │   ├── update_installment_statuses.py  # Update installment due statuses
│   │   └── validate_data.py           # Data validation and fixing
│   ├── migrations/                    # Database migrations
│   ├── static/core/                   # Static files (CSS, JS, images)
│   ├── templates/core/                # HTML templates
│   ├── models.py                      # Database models
│   ├── views.py                       # View functions
│   ├── urls.py                        # URL patterns
│   ├── forms.py                       # Django forms
│   ├── whatsapp_service.py            # Selenium WhatsApp service
│   ├── fee_utils.py                   # Fee calculation utilities
│   ├── signals.py                     # Django signals
│   └── admin.py                       # Django admin configuration
├── fees_management_system/            # Django project settings
│   ├── settings.py                    # Project configuration
│   ├── urls.py                        # Main URL configuration
│   ├── wsgi.py                        # WSGI configuration
│   └── asgi.py                        # ASGI configuration
├── staticfiles/                       # Collected static files
├── logs/                              # Application logs
├── backups/                           # Database backups
├── chrome_profile/                    # Selenium Chrome profile
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Prerequisites

- Python 3.12 recommended
- MySQL Server
- Google Chrome browser (for Selenium WhatsApp automation)
- Windows OS (recommended for batch file automation)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fees_management_system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create MySQL Database
```sql
CREATE DATABASE pclasses;
```

#### Configure Database Settings
Edit `fees_management_system/settings.py` with your database credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pclasses',
        'USER': 'your_mysql_username',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Or use environment variables:

```bash
DB_NAME=pclasses
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### 5. WhatsApp Configuration

Configure your WhatsApp number in `fees_management_system/settings.py`:

```python
MY_WHATSAPP_NUMBER = '+91XXXXXXXXXX'  # Your WhatsApp number for confirmations
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Start Development Server
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000/`

## Usage

### Access Points
- **Main Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Login**: http://localhost:8000/login/

### Default Login
Create a superuser during installation or use Django admin to create users.

### Key Features Usage

#### Student Registration
1. Navigate to the registration page
2. Fill in student personal information
3. Add parent contact details
4. Enter academic information (course, branch)
5. Set up fee structure with installment plan
6. Use auto-fill for equal installment amounts
7. Submit to create student record

#### Fee Management
1. View student details from students list
2. Check installment status and due dates
3. Mark installments as paid
4. Update fee information
5. Track payment history

#### WhatsApp Reminders
1. Use the reminder script for automated reminders:
   ```bash
   python send_whatsapp_reminders_installments.py
   ```
2. Or use batch files:
   ```bash
   start_installment_reminders.bat
   ```
3. Ensure WhatsApp Web is logged in on Chrome
4. Messages are sent based on installment due dates

#### Data Validation
Use the built-in Django management command:
```bash
python manage.py validate_data
```

Apply automatic fixes:
```bash
python manage.py validate_data --fix
```

## WhatsApp Automation

The system uses Selenium WebDriver to automate WhatsApp Web:

### How It Works
1. Chrome browser opens with WhatsApp Web
2. System scans QR code on first use (manual login required)
3. Messages are sent to parent contacts (father and mother)
4. Message delivery is verified via DOM inspection
5. Admin receives confirmation for each message sent

### Reminder Schedule
The system sends reminders at specific intervals:
- **3 days before due date**: Reminder -1
- **1 day after due date**: Reminder -2
- **4 days after due date**: Reminder -3
- **7 days after due date**: Last Reminder
- **10 days after due date**: Discontinuation Notice

### Birthday Messages
- Automatic birthday wishes sent to students on their birthday
- Personalized messages with student's first name
- Sent to parent contact numbers

## Database Schema

### Core Tables
- **student**: Student personal information
- **parent_info**: Parent contact details
- **branch**: Coaching center branches
- **academic_info**: Course and academic details
- **fee_details**: Fee structure and payment tracking
- **fee_installments**: Individual installment records
- **custom_message_log**: WhatsApp message history

### Key Relationships
- Student → ParentInfo (One-to-One)
- Student → AcademicInfo (One-to-One)
- Student → FeeDetails (One-to-One)
- Student → FeeInstallments (One-to-Many)
- Branch → AcademicInfo (One-to-Many)

## Security

- **Environment Variables**: Use .env file for sensitive data
- **Database Credentials**: Never commit database passwords
- **Secret Key**: Keep Django SECRET_KEY secure
- **Session Management**: Django session middleware enabled
- **CSRF Protection**: CSRF middleware enabled

### Environment Variables
Create a `.env` file in the project root:
```
DB_NAME=pclasses
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DJANGO_SECRET_KEY=your_secret_key
MY_WHATSAPP_NUMBER=+91XXXXXXXXXX
```

## Troubleshooting

### Common Issues

#### Database Connection Error
- Verify MySQL server is running
- Check database credentials in settings.py
- Ensure MySQL user has proper permissions

#### WhatsApp Messages Not Sending
- Ensure WhatsApp Web is logged in on Chrome
- Check internet connection
- Verify phone numbers are properly formatted
- Check Chrome profile permissions

#### Selenium Chrome Issues
- Ensure Google Chrome is installed
- Check Chrome profile directory permissions
- Verify selenium package is installed
- Check ChromeDriver compatibility

#### Static Files Not Loading
```bash
python manage.py collectstatic
```

#### Migration Issues
```bash
python manage.py makemigrations --empty core
python manage.py migrate --fake-initial
```

## Batch Files

The project includes several batch files for Windows automation:

- `start_dashboard_only.bat` - Start Django dashboard only
- `start_installment_reminders.bat` - Send installment reminders
- `start_mysql.bat` - Start MySQL server
- `quick_data_check.bat` - Quick data validation
- `scheduled_maintenance.bat` - Scheduled maintenance tasks

## License

This project is created for educational purposes for Pillay Sir's ICSE Classes.

## Support

For technical support:
1. Check the troubleshooting section
2. Review Django documentation
3. Check Selenium WebDriver documentation
4. Verify MySQL connection settings

---

**Fees Management System for Pillay Sir's ICSE Classes**
