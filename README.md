# Gatinos 🐱

**Advanced Cat Colony Management System**

[![Django](https://img.shields.io/badge/Django-4.2.23-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0-green.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Gatinos is a comprehensive Django-based web application designed to manage cat colonies with advanced features for tracking individual cats, their health records, feeding schedules, and volunteer activities. The system supports role-based access control and provides modern web interfaces for efficient colony management.

## 🌟 Features

### 🐈 Core Functionality
- **Individual Cat Profiles**: Complete records with photos, health history, and behavioral notes
- **Colony Management**: Organize cats by geographical colonies with detailed tracking
- **Photo Gallery**: Advanced photo management with automatic thumbnails and EXIF processing
- **Health Records**: Comprehensive veterinary tracking including vaccinations and treatments
- **Activity Logging**: Detailed recording of feeding, sightings, and care activities
- **Interactive Calendar**: Vue.js-powered feeding schedule with real-time updates
- **Report Generation**: Automated reports for veterinary care and colony status

### 👥 User Roles & Access Control
- **🏥 Veterinario (Veterinarian)**: Full medical access, vaccinations, health management
- **🤲 Cuidador (Caretaker)**: Daily care, feeding schedules, basic health recording  
- **👮 Autoridad (Authority)**: Administrative functions, colony management, user oversight
- **👁️ Visitante (Visitor)**: Read-only access to public information and reports

### 🚀 Advanced Features
- **State Machine Workflows**: Track cat status transitions (Free → Captured → Released, etc.)
- **RPC API**: Modern JSON-RPC interface for external integrations
- **Real-time Calendar**: Interactive feeding schedule with color-coded assignments
- **Data Visualization**: Activity heat maps and statistical plots using matplotlib
- **Background Processing**: Celery integration for image processing and reports
- **Multi-Colony Support**: Users can access multiple authorized colonies
- **QR Code Integration**: Quick access to feeding calendars via mobile devices
- **iCalendar Export**: Personal calendar integration for feeding schedules

## 🛠️ Technology Stack

### Backend Infrastructure
- **🐍 Django 4.2.23** - Web framework with custom admin interface
- **🐘 PostgreSQL** - Primary database (SQLite for development)
- **🔄 Celery + Redis** - Background task processing and caching
- **📊 Matplotlib** - Data visualization and activity plotting
- **🖼️ Pillow** - Advanced image processing and thumbnail generation

### Frontend Technologies  
- **⚡ Vue.js 3** - Reactive components for interactive features
- **🏗️ Vite** - Modern frontend build tool and development server
- **📅 v-calendar** - Advanced calendar component library
- **🎨 Custom CSS** - Responsive design with CSS variables

### Specialized Libraries
- **django-viewflow** - State machine workflows for cat status management
- **django-modern-rpc** - JSON-RPC API endpoints
- **django-vite** - Seamless Django-Vite integration
- **icalendar** - Calendar export functionality
- **segno** - QR code generation for mobile access
- **PyYAML** - Configuration management

## 📦 Installation

### System Requirements
- **Python 3.8+** (Python 3.11+ recommended)
- **Node.js 18+** (for frontend development)
- **PostgreSQL 12+** (optional - SQLite works for development)
- **Redis 6+** (for background tasks and caching)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/gatinos.git
cd gatinos

# Build and run with Docker
docker build -t gatinos .
docker run -p 8000:8000 gatinos
```

### Development Setup

1. **Clone and Setup Environment**
   ```bash
   git clone https://github.com/your-org/gatinos.git
   cd gatinos
   
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

3. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your settings
   nano .env
   ```

   **Environment Variables:**
   ```env
   # Core Settings
   SECRET_KEY=your-super-secret-key-here
   DEBUG=True
   TIME_ZONE=Europe/Madrid
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (PostgreSQL)
   SQL_ENGINE=django.db.backends.postgresql
   SQL_DATABASE=gatinos_db
   SQL_USER=gatinos_user
   SQL_PASSWORD=secure_password
   SQL_HOST=localhost
   SQL_PORT=5432
   
   # Redis Configuration
   REDIS_URL=redis://localhost:6379/0
   
   # File Storage
   MEDIA_URL=/media/
   MEDIA_ROOT=/var/www/gatinos/media/
   STATIC_URL=/static/
   STATIC_ROOT=/var/www/gatinos/static/
   
   # Email Configuration (optional)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

4. **Database Setup**
   ```bash
   # Run migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Sync custom permissions
   python manage.py syncpermissions
   
   # Load sample data (optional)
   python manage.py loaddata gatos/fixtures/sample_data.json
   ```

5. **Development Servers**

   **Terminal 1 - Django:**
   ```bash
   python manage.py runserver
   ```
   
   **Terminal 2 - Frontend (for development):**
   ```bash
   cd frontend
   npm run dev
   ```
   
   **Terminal 3 - Background Tasks (optional):**
   ```bash
   celery -A gatinos worker -l info
   ```

6. **Access the Application**
   - **Main Application**: http://localhost:8000
   - **Admin Interface**: http://localhost:8000/admin/
   - **API Documentation**: http://localhost:8000/rpc/

## 🎯 Usage Guide

### Initial Setup Workflow

1. **Admin Configuration**
   - Access admin at `/admin/` with superuser credentials
   - Create user groups: `cuidador`, `veterinario`, `autoridad`, `visitante`
   - Configure permissions for each group

2. **Colony Setup**
   - Create colonies in the admin interface
   - Set up authorized users for each colony
   - Configure colony-specific settings

3. **User Management**
   - Create user accounts via admin interface
   - Assign users to appropriate groups
   - Grant colony access permissions

### Day-to-Day Operations

#### For Caretakers (Cuidadores)
```
1. Log feeding activities via interactive calendar
2. Upload photos of cats and colony activities  
3. Record cat sightings and behavioral observations
4. Update basic health information during visits
```

#### For Veterinarians (Veterinarios)
```
1. Manage comprehensive health records
2. Track vaccination schedules and treatments
3. Record capture/release workflows
4. Generate health reports for authorities
```

#### For Authorities (Autoridades)
```
1. Monitor overall colony health and population
2. Generate reports for city councils or NGOs
3. Manage user access and permissions
4. Coordinate between multiple colonies
```

### Key Features Deep Dive

#### 📅 Interactive Calendar System
- **Color Coding**: Red (your assignments), Yellow (others), Gray (unassigned)
- **Real-time Updates**: Changes sync immediately across all users
- **Mobile Access**: QR codes for quick mobile calendar access
- **Export Options**: iCal format for personal calendar integration

#### 🏥 Health Tracking Workflow
```
Cat Registration → Health Assessment → Vaccination Schedule → 
Treatment Records → Recovery Monitoring → Release Documentation
```

#### 📊 Data Visualization
- **Activity Heat Maps**: Visual representation of colony activity patterns
- **Health Statistics**: Vaccination rates, treatment outcomes
- **Population Trends**: Colony growth/decline over time
- **User Contributions**: Individual volunteer activity tracking

## 🔌 API Reference

### RPC Endpoints

The application provides JSON-RPC endpoints at `/rpc/`:

#### Calendar Management
```javascript
// Toggle feeding assignment
{
  "method": "toggle_feeding_date",
  "params": {
    "date_str": "2024-01-15",
    "colonia_id": 1,
    "current_color": "none"
  }
}

// Get feeding schedule
{
  "method": "get_feeding_dates", 
  "params": {
    "colonia_id": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

#### Colony Access
```javascript
// Check user permissions
{
  "method": "colony_access_check",
  "params": {
    "colonia_id": 1,
    "user_id": 123
  }
}
```

### Frontend Integration

```javascript
// Example Vue.js integration
export async function toggleFeedingDate(date, coloniaId) {
  const response = await fetch('/rpc/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
      method: 'toggle_feeding_date',
      params: { date_str: date, colonia_id: coloniaId }
    })
  });
  
  return response.json();
}
```

## 🏗️ Project Architecture

```
gatinos/
├── 🐍 Backend (Django)
│   ├── gatinos/              # Main project configuration
│   │   ├── settings.py       # Django settings with environment configs
│   │   ├── urls.py          # URL routing
│   │   ├── admin.py         # Custom admin site configuration
│   │   └── wsgi.py          # WSGI application
│   ├── gatos/               # Core cat management application  
│   │   ├── models.py        # Data models (Cat, Colony, Health, etc.)
│   │   ├── views.py         # Class-based views with mixins
│   │   ├── admin.py         # Admin interface customization
│   │   ├── rpc.py          # JSON-RPC API endpoints
│   │   ├── plots.py        # Data visualization functions
│   │   ├── flows.py        # State machine workflows
│   │   ├── forms.py        # Django forms
│   │   ├── tasks.py        # Celery background tasks
│   │   └── templates/      # HTML templates
│   ├── registration/        # User authentication system
│   └── utils/              # Shared utilities
├── 🎨 Frontend (Vue.js)
│   ├── src/
│   │   ├── main.js         # Vue application entry point
│   │   └── components/     # Vue components
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js     # Vite configuration
├── 🗄️ Database
│   └── migrations/         # Database schema migrations
├── 📁 Static Assets
│   ├── css/               # Custom stylesheets
│   ├── js/                # JavaScript utilities
│   └── images/            # Static images
└── 🐳 Deployment
    ├── Dockerfile         # Container configuration
    ├── requirements.txt   # Python dependencies
    └── entrypoint.sh     # Container startup script
```

## 🚀 Deployment

### Production Deployment with Docker

```bash
# Production build
docker build -t gatinos:production .

# Run with environment variables
docker run -d \
  --name gatinos-app \
  -p 8000:8000 \
  -e SECRET_KEY="production-secret-key" \
  -e DEBUG=False \
  -e SQL_ENGINE="django.db.backends.postgresql" \
  -e SQL_DATABASE="gatinos_prod" \
  -e SQL_USER="gatinos_user" \
  -e SQL_PASSWORD="secure_password" \
  -e SQL_HOST="db.example.com" \
  gatinos:production
```

### Traditional Server Deployment

1. **Web Server Configuration (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location /static/ {
           alias /var/www/gatinos/static/;
       }
       
       location /media/ {
           alias /var/www/gatinos/media/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Application Server (Gunicorn)**
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:8000 gatinos.wsgi:application
   ```

3. **Background Workers (Systemd)**
   ```ini
   # /etc/systemd/system/gatinos-celery.service
   [Unit]
   Description=Gatinos Celery Worker
   After=network.target
   
   [Service]
   Type=forking
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/gatinos
   Environment=DJANGO_SETTINGS_MODULE=gatinos.settings
   ExecStart=/var/www/gatinos/.venv/bin/celery -A gatinos worker -l info
   
   [Install]
   WantedBy=multi-user.target
   ```

### Performance Optimization

- **Database**: Use PostgreSQL with connection pooling
- **Caching**: Redis for session storage and view caching  
- **Static Files**: CDN for static asset delivery
- **Image Processing**: Background task processing for thumbnails
- **Monitoring**: Use Django Debug Toolbar in development

## 🧪 Development

### Code Quality Standards

```bash
# Python formatting and linting
black .
isort .
flake8 .

# Frontend linting  
cd frontend
npm run lint
npm run format
```

### Testing

```bash
# Run Django tests
python manage.py test

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report

# Frontend tests (if configured)
cd frontend  
npm test
```

### Adding New Features

1. **Database Models**: Update `models.py` and create migrations
2. **Admin Interface**: Customize admin forms and list views
3. **API Endpoints**: Add RPC methods for frontend integration
4. **Frontend Components**: Create Vue.js components for interactivity
5. **Templates**: Design responsive HTML templates
6. **Permissions**: Define custom permissions for user roles

### Development Workflow

```bash
# Feature development
git checkout -b feature/new-health-tracking
python manage.py makemigrations
python manage.py migrate
# ... develop and test ...
git commit -m "Add advanced health tracking features"
git push origin feature/new-health-tracking
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes with appropriate tests
5. **Commit** with descriptive messages: `git commit -m 'Add amazing feature'`
6. **Push** to your branch: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request with detailed description

### Code Standards
- **Python**: Follow PEP 8, use type hints where applicable
- **JavaScript**: Use ESLint configuration, prefer modern ES6+ syntax
- **Documentation**: Update README.md and add docstrings for new functions
- **Testing**: Add tests for new functionality
- **Commit Messages**: Use conventional commit format

### Issue Reporting
- Use GitHub Issues for bug reports and feature requests
- Include detailed steps to reproduce issues
- Provide system information and error logs
- Label issues appropriately (bug, enhancement, documentation)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
Copyright (c) 2024 Gatinos Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

## 🙏 Acknowledgments

- **Django Community** - For the robust web framework
- **Vue.js Team** - For the reactive frontend library  
- **Open Source Contributors** - All the amazing libraries we depend on
- **Cat Colony Volunteers** - The real heroes who inspired this project
- **Veterinary Professionals** - For guidance on health tracking requirements

## 📞 Support & Community

### Getting Help
- **📚 Documentation**: Check this README and inline code documentation
- **🐛 Bug Reports**: Open an issue on GitHub with detailed information
- **💡 Feature Requests**: Use GitHub Issues with the "enhancement" label
- **💬 Discussions**: Join our community discussions for general questions

### Contact Information
- **Project Maintainer**: [Your Name](mailto:your-email@example.com)
- **GitHub Issues**: [Report Issues](https://github.com/your-org/gatinos/issues)
- **Community Forum**: [Join Discussions](https://github.com/your-org/gatinos/discussions)

---

**Made with ❤️ for cat colony volunteers and the cats they care for.**

*"In the eyes of a cat, all things belong to cats." - Unknown*