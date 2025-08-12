# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gatinos is a Django-based web application for managing cat colonies. It's designed for Spanish-speaking users and includes features for tracking cats, health records, feeding schedules, and volunteer activities.

## Development Environment

The project uses a Python virtual environment located at `.venv/`. Always use this environment for Python/Django commands.

## Development Commands

```bash
# Activate virtual environment (if needed)
source .venv/bin/activate

# Run development server
python manage.py runserver

# Run Vite development server (in frontend directory)
cd frontend && npm run dev

# Run tests
python manage.py test

# Run Django system checks
python manage.py check

# Apply database migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Sync custom permissions (required after initial setup)
python manage.py syncpermissions

# Create superuser for admin access
python manage.py createsuperuser

# Collect static files for production
python manage.py collectstatic

# Start Django shell for debugging
python manage.py shell
```

## Architecture & Key Components

### Core Apps

- **gatos/**: Main app handling cats, colonies, photos, health records, and activities
  - `models.py`: Defines Gato, Colonia, Foto, Informe, Enfermedad, Captura, Vacunacion, etc.
  - `views.py`: Contains all view controllers for the web interface
  - `forms.py`: Form definitions for data input
  - `activity.py`: Activity tracking functionality
  - `rpc.py`: RPC API endpoints using django-modern-rpc
  - `flows.py`: Workflow definitions using django-viewflow

- **registration/**: User authentication and role management
  - Custom permission groups: cuidador, veterinario, autoridad, visitante
  - Management command: `syncpermissions` syncs groups defined in settings

- **utils/**: Shared utilities and context processors

### Data Models

The main entities and their relationships:
- **Colonia** (Colony): Geographic area containing cats
- **Gato** (Cat): Individual cat with state machine (LIBRE, CAPTURADO, DESAPARECIDO, OLVIDADO, MUERTO)
- **Foto** (Photo): Images linked to cats or colonies
- **Informe** (Report): Text reports about cats or colonies
- **Enfermedad** (Illness): Health conditions and treatments
- **Captura** (Capture): Records of cat captures for medical procedures
- **Vacunacion** (Vaccination): Vaccination records linked to captures
- **Avistamiento** (Sighting): Cat sighting records
- **AsignacionComida** (Feeding): Scheduled feeding assignments

### Permission System

Role-based access control configured in `settings.py` under `GROUPS_PERMISSIONS`:
- **cuidador**: Basic caretaker permissions (view, add photos/reports, feed, sight)
- **veterinario**: Medical permissions (vaccinate, manage health records, add cats)
- **autoridad**: Administrative permissions (manage colonies, capture/release cats)
- **visitante**: Read-only access

### Key Configuration

- Language: Spanish (es-es)
- Timezone: Configurable via TIME_ZONE env var (default: Europe/Madrid)
- Database: PostgreSQL in production, SQLite for development
- Media storage: Configurable via STORAGES_BACKEND
- Background tasks: Celery with Redis
- Template engine: Django templates with custom form renderer

### External Dependencies

- **django-plottings**: Data visualization (installed from GitHub)
- **django-viewflow**: Workflow management
- **django-modern-rpc**: RPC API functionality
- **django-vite**: Integration with Vite for Vue components
- **Celery**: Asynchronous task processing
- **Pillow**: Image processing

### Frontend Integration

The project includes a Vue.js frontend setup in the `frontend/` directory:
- **Vite**: Build tool for Vue components
- **Vue 3**: Component framework
- **v-calendar**: Calendar component library

Django-vite is configured to:
- Use Vite dev server in development (port 5173)
- Build and serve compiled assets in production
- Enable hot module replacement for Vue components

## Important Notes

- The interface is primarily in Spanish to serve the target community
- All model names and user-facing content use Spanish terminology
- The app uses Django's built-in admin interface for user management
- Custom templates override Django defaults for forms and widgets
- State transitions for cats are managed through the EstadoGato choices
- Photos can extract EXIF data for automatic date/location information