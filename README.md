# Gatinos 🐱

**Aplicación para la Gestión de Colonias de Gatos**

Gatinos is a Django-based web application designed to manage cat colonies, track individual cats, their health records, feeding schedules, and volunteer activities. The system supports role-based access control for different types of users including caretakers, veterinarians, authorities, and visitors.

## Features

### Core Functionality
- **Cat Management**: Register and track individual cats with detailed profiles
- **Colony Management**: Organize cats by colonies with location tracking
- **Photo Gallery**: Upload and manage photos of cats and colonies
- **Health Records**: Track vaccinations, illnesses, and veterinary interventions
- **Activity Logging**: Record feeding, sightings, and general care activities
- **Reports**: Generate detailed reports on colony activities and cat status

### User Roles & Permissions
- **Cuidador (Caretaker)**: View colonies/cats, add photos/reports, feed colonies, record sightings
- **Veterinario (Veterinarian)**: All caretaker permissions plus manage cat health, vaccinations, add new cats
- **Autoridad (Authority)**: Manage colonies, capture/release cats, access to administrative functions
- **Visitante (Visitor)**: Read-only access to view colonies, cats, photos, and reports

### Advanced Features
- **State Management**: Track cat status (Free, Captured, Missing, Dead, etc.)
- **Calendar Integration**: Schedule and track feeding activities
- **RPC API**: Modern RPC interface for external integrations
- **Plotting & Analytics**: Visual data representation using django-plottings
- **Celery Integration**: Background task processing
- **Workflow Management**: Using django-viewflow for complex processes

## Technology Stack

- **Backend**: Django 4.2.23
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Task Queue**: Celery with Redis
- **Image Processing**: Pillow
- **Additional Libraries**:
  - django-storages (cloud storage support)
  - django-viewflow (workflow management)
  - django-modern-rpc (API endpoints)
  - icalendar (calendar functionality)
  - segno (QR code generation)
  - PyYAML (configuration files)

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite works for development)
- Redis (for Celery tasks)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gatinos
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create a .env file or set environment variables
   export SECRET_KEY="your-secret-key-here"
   export DEBUG=1
   export TIME_ZONE="Europe/Madrid"
   
   # Database configuration (optional - defaults to SQLite)
   export SQL_ENGINE="django.db.backends.postgresql"
   export SQL_DATABASE="gatinos_db"
   export SQL_USER="your_user"
   export SQL_PASSWORD="your_password"
   export SQL_HOST="localhost"
   export SQL_PORT="5432"
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Sync permissions**
   ```bash
   python manage.py syncpermissions
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Docker Support

The project includes Docker configuration for easy deployment:

```bash
# Build and run with Docker
docker build -t gatinos .
docker run -p 8000:8000 gatinos
```

## Usage

### Basic Workflow

1. **Create Colonies**: Set up geographical areas where cat colonies are located
2. **Register Cats**: Add individual cats to colonies with photos and descriptions
3. **Track Activities**: Log feeding schedules, health checkups, and sightings
4. **Manage Health**: Record vaccinations, treatments, and medical conditions
5. **Generate Reports**: Create reports on colony status and activities

### User Management

Access the admin panel at `/admin/` to:
- Create user accounts
- Assign users to appropriate groups (cuidador, veterinario, autoridad, visitante)
- Manage permissions and access levels

### API Access

The application provides RPC endpoints for external integrations:
- Endpoint: `/rpc/`
- Documentation: Available through the admin interface

## Project Structure

```
gatinos/
├── gatinos/           # Main Django project
│   ├── settings.py    # Configuration
│   ├── urls.py        # URL routing
│   └── templates/     # Base templates
├── gatos/             # Core cat management app
│   ├── models.py      # Data models
│   ├── views.py       # View controllers
│   ├── forms.py       # Form definitions
│   ├── templates/     # App templates
│   └── data/          # Configuration data
├── registration/      # User authentication
├── utils/             # Utility functions
├── requirements.txt   # Python dependencies
└── manage.py         # Django management script
```

## Configuration

### Key Settings

- **Language**: Spanish (es-es)
- **Timezone**: Europe/Madrid (configurable via TIME_ZONE env var)
- **Media Storage**: Configurable via STORAGES_BACKEND
- **Static Files**: Configurable via STATICFILES_STORAGES_BACKEND

### Custom Permissions

The application uses custom permission groups defined in `settings.py` to control access to various features based on user roles.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For support, bug reports, or feature requests, please open an issue on the project repository.

---

**Note**: This application is designed for Spanish-speaking users managing cat colonies, with the interface and documentation primarily in Spanish to serve the target community effectively.
