# 🎓 Pillay Sir's ICSE Classes - Fees Management System

A complete Django-based fees management system with Neural Glass theme and WhatsApp integration for coaching classes.

## ✨ Features

### 🏠 Dashboard
- **Futuristic Neural Glass UI** with glowing effects and animations
- **Real-time Statistics** - Total students, fees collected, pending fees, overdue students
- **Quick Action Cards** with hover animations
- **Recent Activities** table with student information

### 👥 Student Management
- **Complete Student Registration** with all required fields
- **Student Directory** with search and filter functionality
- **Detailed Student Profiles** with personal, academic, and fee information
- **Parent Information** management with contact details

### 💰 Fee Management
- **Fee Tracking** with installment support
- **Payment Updates** with payment history
- **Fee Status Monitoring** (Paid/Pending/Overdue)
- **Multiple Payment Methods** support

### 📱 WhatsApp Integration
- **Automated Reminders** via PyWhatKit (no external API required)
- **Bulk Message Sending** to multiple parents with multi-select
- **Windows Task Scheduler** integration for daily automation
- **Manual Trigger** from dashboard for instant reminders
- **Smart Due Date Detection** (sends reminders 2 days before due)
- **Comprehensive Logging** with CSV tracking
- **Message Templates** for different scenarios
- **Real-time Message Status** tracking

### 📊 Reports & Analytics
- **PDF Report Generation** using ReportLab
- **Course-wise Analytics** with visual progress bars
- **Fee Collection Reports** with detailed breakdowns
- **Student Directory** exports
- **Monthly Summary** reports

### 🔐 Authentication & Security
- **Admin/Staff Login System** with role-based access
- **Secure Session Management**
- **CSRF Protection** enabled

## 🛠️ Technology Stack

- **Backend**: Django 5.2.7
- **Database**: MySQL with custom schema
- **Frontend**: Bootstrap 5 + Neural Glass Theme
- **WhatsApp**: PyWhatKit + Pandas (no external API)
- **PDF Generation**: ReportLab + xhtml2pdf
- **Data Processing**: Pandas for student data analysis
- **Automation**: Windows Task Scheduler integration
- **Icons**: Font Awesome 6
- **Animations**: Custom CSS animations

## 📋 Prerequisites

- Python 3.8+
- MySQL Server
- WhatsApp Web access (for PyWhatKit integration)
- Windows OS (for Task Scheduler automation)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fees_management_system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create MySQL Database
```sql
CREATE DATABASE pclasses;
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON pclasses.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Update Database Settings
Edit `fees_management_system/settings.py`:
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

### 5. WhatsApp Configuration (Optional)

#### Get Twilio Credentials
1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token
3. Set up WhatsApp Sandbox

#### Update Twilio Settings
Edit `fees_management_system/settings.py`:
```python
TWILIO_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'  # Sandbox number
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Sample Data
```bash
python manage.py populate_sample_data
```

### 8. Start Development Server
```bash
python manage.py runserver
```

## 🎯 Usage

### Access the Application
- **Main Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

### Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Key URLs
- `/` - Dashboard
- `/register/` - Student Registration
- `/students/` - Students List
- `/fees/` - Fee Management
- `/whatsapp/` - WhatsApp Panel
- `/reports/` - Reports & Analytics

## 📱 WhatsApp Features

### Message Templates
1. **Fee Reminder**: Standard payment reminder
2. **Urgent Payment**: For overdue fees
3. **Installment Due**: Next installment reminder
4. **Custom Message**: Personalized messages

### Available Variables
- `[Father_Name]` - Father's name
- `[Student_Name]` - Student's full name
- `[Pending_Amount]` - Outstanding fee amount
- `[Course]` - Enrolled course

## 📊 Database Schema

### Core Tables
- **Student**: Personal information and registration details
- **Parent_Info**: Parent contact and occupation details
- **Branch**: Coaching center branches
- **Academic_Info**: Course and academic details
- **Fee_Details**: Fee structure and payment tracking

### Relationships
- Student → Parent_Info (One-to-One)
- Student → Academic_Info (One-to-One)
- Student → Fee_Details (One-to-One)
- Branch → Academic_Info (One-to-Many)

## 🎨 Neural Glass Theme

### Features
- **Glassmorphism Effects** with backdrop blur
- **Neon Glowing Elements** with CSS animations
- **Particle Background** with JavaScript canvas
- **Smooth Transitions** and hover effects
- **Responsive Design** for all screen sizes

### Color Scheme
- **Primary**: Neon Blue (#00f5ff)
- **Secondary**: Neon Pink (#ff006e)
- **Accent**: Purple (#8338ec)
- **Background**: Dark with gradients

## 📈 Reports Available

1. **Fee Collection Report**: Complete payment tracking
2. **Student Directory**: All student information
3. **Overdue Fees Report**: Students with pending payments
4. **Course-wise Analytics**: Enrollment and revenue by course
5. **Individual Receipts**: Student-specific payment receipts
6. **Monthly Summary**: Month-wise revenue analysis

## 🔧 Customization

### Adding New Courses
Update the course choices in `core/templates/core/registration.html`:
```html
<option value="New Course">New Course</option>
```

### Modifying Fee Structure
Update fee calculation logic in `core/views.py` and templates.

### Custom Message Templates
Add new templates in `core/templates/core/whatsapp_panel.html`.

## 🐛 Troubleshooting

### Common Issues

#### MySQL Connection Error
- Verify MySQL server is running
- Check database credentials in settings.py
- Ensure MySQL user has proper permissions

#### WhatsApp Messages Not Sending
- Verify Twilio credentials
- Check WhatsApp sandbox setup
- Ensure phone numbers are properly formatted

#### Static Files Not Loading
```bash
python manage.py collectstatic
```

#### Migration Issues
```bash
python manage.py makemigrations --empty core
python manage.py migrate --fake-initial
```

## 📝 Development Notes

### Project Structure
```
fees_management_system/
├── core/                          # Main Django app
│   ├── management/commands/       # Custom management commands
│   ├── static/core/              # Static files (CSS, JS)
│   ├── templates/core/           # HTML templates
│   ├── models.py                 # Database models
│   ├── views.py                  # View functions
│   ├── urls.py                   # URL patterns
│   └── forms.py                  # Django forms
├── fees_management_system/        # Project settings
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

### Key Components
- **Neural Glass Theme**: Custom CSS with glassmorphism effects
- **JavaScript Animations**: Particle backgrounds and interactions
- **Django Models**: MySQL-compatible with proper relationships
- **Twilio Integration**: WhatsApp messaging functionality
- **PDF Generation**: ReportLab for receipt and report creation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is created for educational purposes. Please ensure you have proper licenses for any third-party services used (Twilio, etc.).

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review Django and Twilio documentation
3. Create an issue in the repository

## 🎉 Acknowledgments

- **Neural Glass Theme**: Inspired by modern glassmorphism design trends
- **Django Community**: For the excellent web framework
- **Twilio**: For WhatsApp API integration
- **Bootstrap**: For responsive UI components

---

**Made with ❤️ for Pillay Sir's ICSE Classes**

*Ready-to-run fees management system with beautiful Neural Glass UI and WhatsApp integration!*
