# Gatinos 🐈

## Aviso del Programador

Se planea que este proyecto esté listo para ser usado cuando se cree la aplicación móvil que la acompaña, mientrastanto la estoy usando para practicar las últimas técnicas de programación con LLMs añadiendo características y refactorizando.

**Sistema Avanzado de Gestión de Colonias Felinas**

[![Django](https://img.shields.io/badge/Django-4.2.23-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0-green.svg)](https://vuejs.org/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)

Gatinos es una aplicación web integral basada en Django diseñada para gestionar colonias de gatos con características avanzadas para el seguimiento de gatos individuales, sus registros de salud, horarios de alimentación y actividades de voluntarios. El sistema soporta control de acceso basado en roles y proporciona interfaces web modernas para una gestión eficiente de colonias.

## Características

### 🐈 Funcionalidad Principal
- **Perfiles Individuales de Gatos**: Registros completos con fotos, historial de salud y notas de comportamiento
- **Gestión de Colonias**: Organización de gatos por colonias geográficas con seguimiento detallado
- **Galería de Fotos**: Gestión avanzada de fotos con miniaturas automáticas y procesamiento EXIF
- **Registros de Salud**: Seguimiento veterinario completo incluyendo vacunaciones y tratamientos
- **Registro de Actividades**: Grabación detallada de alimentación, avistamientos y actividades de cuidado
- **Calendario Interactivo**: Horario de alimentación con Vue.js y actualizaciones en tiempo real
- **Generación de Informes**: Informes automatizados para cuidado veterinario y estado de colonias

### 👥 Roles de Usuario y Control de Acceso
- **🏥 Veterinario**: Acceso médico completo, vacunaciones, gestión de salud
- **🤲 Cuidador**: Cuidado diario, horarios de alimentación, registro básico de salud
- **👮 Autoridad**: Funciones administrativas, gestión de colonias, supervisión de usuarios
- **👁️ Visitante**: Acceso de solo lectura a información pública e informes

### 🚀 Características Avanzadas
- **Flujos de Estado**: Seguimiento de transiciones de estado de gatos (Libre → Capturado → Liberado, etc.)
- **API RPC**: Interfaz JSON-RPC moderna para integraciones externas
- **Calendario en Tiempo Real**: Horario de alimentación interactivo con asignaciones codificadas por colores
- **Visualización de Datos**: Mapas de calor de actividad y gráficos estadísticos usando matplotlib
- **Procesamiento en Segundo Plano**: Integración con Celery para procesamiento de imágenes e informes
- **Soporte Multi-Colonia**: Los usuarios pueden acceder a múltiples colonias autorizadas
- **Integración de Códigos QR**: Acceso rápido a calendarios de alimentación vía dispositivos móviles
- **Exportación iCalendar**: Integración con calendario personal para horarios de alimentación

## 🛠️ Stack Tecnológico

### Infraestructura Backend
- **🐍 Django 4.2.23** - Framework web con interfaz de administración personalizada
- **🐘 PostgreSQL** - Base de datos principal (SQLite para desarrollo)
- **🔄 Celery + Redis** - Procesamiento de tareas en segundo plano y caché
- **📊 Matplotlib** - Visualización de datos y gráficos de actividad
- **🖼️ Pillow** - Procesamiento avanzado de imágenes y generación de miniaturas

### Tecnologías Frontend
- **⚡ Vue.js 3** - Componentes reactivos para características interactivas
- **🏗️ Vite** - Herramienta moderna de construcción y servidor de desarrollo frontend
- **📅 v-calendar** - Biblioteca avanzada de componentes de calendario
- **🎨 CSS Personalizado** - Diseño responsivo con variables CSS

### Librerías Especializadas
- **django-viewflow** - Flujos de trabajo de máquina de estados para gestión del estado de gatos
- **django-modern-rpc** - Endpoints de API JSON-RPC
- **django-vite** - Integración perfecta Django-Vite
- **icalendar** - Funcionalidad de exportación de calendario
- **segno** - Generación de códigos QR para acceso móvil
- **PyYAML** - Gestión de configuración

## 📦 Instalación

### Requisitos del Sistema
- **Python 3.8+** (Se recomienda Python 3.11+)
- **Node.js 18+** (para desarrollo frontend)
- **PostgreSQL 12+** (opcional - SQLite funciona para desarrollo)
- **Redis 6+** (para tareas en segundo plano y caché)

### Inicio Rápido con Docker

```bash
# Clonar el repositorio
git clone https://github.com/tu-org/gatinos.git
cd gatinos

# Construir y ejecutar con Docker
docker build -t gatinos .
docker run -p 8000:8000 gatinos
```

### Configuración para Desarrollo

1. **Clonar y Configurar el Entorno**
   ```bash
   git clone https://github.com/tu-org/gatinos.git
   cd gatinos
   
   # Crear entorno virtual
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Instalar Dependencias**
   ```bash
   # Dependencias de Python
   pip install -r requirements.txt
   
   # Dependencias del frontend
   cd frontend
   npm install
   cd ..
   ```

3. **Configurar el Entorno**
   ```bash
   # Copiar plantilla de entorno
   cp .env.example .env
   
   # Editar .env con tu configuración
   nano .env
   ```

   **Variables de Entorno:**
   ```env
   # Configuración Principal
   SECRET_KEY=tu-clave-super-secreta-aqui
   DEBUG=True
   TIME_ZONE=Europe/Madrid
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Base de Datos (PostgreSQL)
   SQL_ENGINE=django.db.backends.postgresql
   SQL_DATABASE=gatinos_db
   SQL_USER=gatinos_user
   SQL_PASSWORD=contraseña_segura
   SQL_HOST=localhost
   SQL_PORT=5432
   
   # Configuración de Redis
   REDIS_URL=redis://localhost:6379/0
   
   # Almacenamiento de Archivos
   MEDIA_URL=/media/
   MEDIA_ROOT=/var/www/gatinos/media/
   STATIC_URL=/static/
   STATIC_ROOT=/var/www/gatinos/static/
   
   # Configuración de Email (opcional)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-contraseña-app
   ```

4. **Configuración de Base de Datos**
   ```bash
   # Ejecutar migraciones
   python manage.py migrate
   
   # Crear superusuario
   python manage.py createsuperuser
   
   # Sincronizar permisos personalizados
   python manage.py syncpermissions
   
   # Cargar datos de ejemplo (opcional)
   python manage.py loaddata gatos/fixtures/sample_data.json
   ```

5. **Servidores de Desarrollo**

   **Terminal 1 - Django:**
   ```bash
   python manage.py runserver
   ```
   
   **Terminal 2 - Frontend (para desarrollo):**
   ```bash
   cd frontend
   npm run dev
   ```
   
   **Terminal 3 - Tareas en Segundo Plano (opcional):**
   ```bash
   celery -A gatinos worker -l info
   ```

6. **Acceder a la Aplicación**
   - **Aplicación Principal**: http://localhost:8000
   - **Interfaz de Administración**: http://localhost:8000/admin/
   - **Documentación API**: http://localhost:8000/rpc/

## 🎯 Guía de Uso

### Flujo de Configuración Inicial

1. **Configuración de Administración**
   - Acceder al admin en `/admin/` con credenciales de superusuario
   - Crear grupos de usuarios: `cuidador`, `veterinario`, `autoridad`, `visitante`
   - Configurar permisos para cada grupo

2. **Configuración de Colonias**
   - Crear colonias en la interfaz de administración
   - Configurar usuarios autorizados para cada colonia
   - Configurar ajustes específicos de colonia

3. **Gestión de Usuarios**
   - Crear cuentas de usuario vía interfaz de administración
   - Asignar usuarios a grupos apropiados
   - Otorgar permisos de acceso a colonias

### Operaciones Diarias

#### Para Cuidadores
```
1. Registrar actividades de alimentación vía calendario interactivo
2. Subir fotos de gatos y actividades de la colonia
3. Registrar avistamientos de gatos y observaciones de comportamiento
4. Actualizar información básica de salud durante visitas
```

#### Para Veterinarios
```
1. Gestionar registros completos de salud
2. Seguimiento de calendarios de vacunación y tratamientos
3. Registrar flujos de captura/liberación
4. Generar informes de salud para autoridades
```

#### Para Autoridades
```
1. Monitorear salud general y población de colonias
2. Generar informes para ayuntamientos u ONGs
3. Gestionar acceso de usuarios y permisos
4. Coordinar entre múltiples colonias
```

### Características Clave en Detalle

#### 📅 Sistema de Calendario Interactivo
- **Codificación por Colores**: Rojo (tus asignaciones), Amarillo (otros), Gris (sin asignar)
- **Actualizaciones en Tiempo Real**: Los cambios se sincronizan inmediatamente entre todos los usuarios
- **Acceso Móvil**: Códigos QR para acceso rápido al calendario móvil
- **Opciones de Exportación**: Formato iCal para integración con calendario personal

#### 🏥 Flujo de Seguimiento de Salud
```
Registro de Gato → Evaluación de Salud → Calendario de Vacunación → 
Registros de Tratamiento → Monitoreo de Recuperación → Documentación de Liberación
```

#### 📊 Visualización de Datos
- **Mapas de Calor de Actividad**: Representación visual de patrones de actividad de colonias
- **Estadísticas de Salud**: Tasas de vacunación, resultados de tratamientos
- **Tendencias de Población**: Crecimiento/disminución de colonias en el tiempo
- **Contribuciones de Usuarios**: Seguimiento de actividad de voluntarios individuales

## 🔌 Referencia de API

### Endpoints RPC

La aplicación proporciona endpoints JSON-RPC en `/rpc/`:

#### Gestión de Calendario
```javascript
// Alternar asignación de alimentación
{
  "method": "toggle_feeding_date",
  "params": {
    "date_str": "2024-01-15",
    "colonia_id": 1,
    "current_color": "none"
  }
}

// Obtener horario de alimentación
{
  "method": "get_feeding_dates", 
  "params": {
    "colonia_id": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

#### Acceso a Colonias
```javascript
// Verificar permisos de usuario
{
  "method": "colony_access_check",
  "params": {
    "colonia_id": 1,
    "user_id": 123
  }
}
```

### Integración Frontend

```javascript
// Ejemplo de integración con Vue.js
export async function alternarFechaAlimentacion(fecha, coloniaId) {
  const response = await fetch('/rpc/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': obtenerCsrfToken()
    },
    body: JSON.stringify({
      method: 'toggle_feeding_date',
      params: { date_str: fecha, colonia_id: coloniaId }
    })
  });
  
  return response.json();
}
```

## 🏗️ Arquitectura del Proyecto

```
gatinos/
├── 🐍 Backend (Django)
│   ├── gatinos/              # Configuración principal del proyecto
│   │   ├── settings.py       # Ajustes de Django con configuraciones de entorno
│   │   ├── urls.py          # Enrutamiento de URLs
│   │   ├── admin.py         # Configuración personalizada del sitio admin
│   │   └── wsgi.py          # Aplicación WSGI
│   ├── gatos/               # Aplicación principal de gestión de gatos
│   │   ├── models.py        # Modelos de datos (Gato, Colonia, Salud, etc.)
│   │   ├── views.py         # Vistas basadas en clases con mixins
│   │   ├── admin.py         # Personalización de interfaz admin
│   │   ├── rpc.py          # Endpoints de API JSON-RPC
│   │   ├── plots.py        # Funciones de visualización de datos
│   │   ├── flows.py        # Flujos de trabajo de máquina de estados
│   │   ├── forms.py        # Formularios Django
│   │   ├── tasks.py        # Tareas Celery en segundo plano
│   │   └── templates/      # Plantillas HTML
│   ├── registration/        # Sistema de autenticación de usuarios
│   └── utils/              # Utilidades compartidas
├── 🎨 Frontend (Vue.js)
│   ├── src/
│   │   ├── main.js         # Punto de entrada de la aplicación Vue
│   │   └── components/     # Componentes Vue
│   ├── package.json        # Dependencias Node.js
│   └── vite.config.js     # Configuración de Vite
├── 🗄️ Base de Datos
│   └── migrations/         # Migraciones del esquema de base de datos
├── 📁 Archivos Estáticos
│   ├── css/               # Hojas de estilo personalizadas
│   ├── js/                # Utilidades JavaScript
│   └── images/            # Imágenes estáticas
└── 🐳 Despliegue
    ├── Dockerfile         # Configuración del contenedor
    ├── requirements.txt   # Dependencias Python
    └── entrypoint.sh     # Script de inicio del contenedor
```

## 🚀 Despliegue

### Despliegue en Producción con Docker

```bash
# Construcción para producción
docker build -t gatinos:production .

# Ejecutar con variables de entorno
docker run -d \
  --name gatinos-app \
  -p 8000:8000 \
  -e SECRET_KEY="clave-secreta-produccion" \
  -e DEBUG=False \
  -e SQL_ENGINE="django.db.backends.postgresql" \
  -e SQL_DATABASE="gatinos_prod" \
  -e SQL_USER="gatinos_user" \
  -e SQL_PASSWORD="contraseña_segura" \
  -e SQL_HOST="db.ejemplo.com" \
  gatinos:production
```

### Despliegue Tradicional en Servidor

1. **Configuración del Servidor Web (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name tu-dominio.com;
       
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

2. **Servidor de Aplicación (Gunicorn)**
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:8000 gatinos.wsgi:application
   ```

3. **Workers en Segundo Plano (Systemd)**
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

### Optimización de Rendimiento

- **Base de Datos**: Usar PostgreSQL con pooling de conexiones
- **Caché**: Redis para almacenamiento de sesiones y caché de vistas
- **Archivos Estáticos**: CDN para entrega de archivos estáticos
- **Procesamiento de Imágenes**: Procesamiento de tareas en segundo plano para miniaturas
- **Monitoreo**: Usar Django Debug Toolbar en desarrollo

## 🧪 Desarrollo

### Estándares de Calidad de Código

```bash
# Formateo y linting de Python
black .
isort .
flake8 .

# Linting del frontend
cd frontend
npm run lint
npm run format
```

### Testing

```bash
# Ejecutar tests de Django
python manage.py test

# Ejecutar tests con cobertura
coverage run --source='.' manage.py test
coverage report

# Tests del frontend (si están configurados)
cd frontend
npm test
```

### Agregar Nuevas Características

1. **Modelos de Base de Datos**: Actualizar `models.py` y crear migraciones
2. **Interfaz de Administración**: Personalizar formularios y vistas de lista del admin
3. **Endpoints API**: Agregar métodos RPC para integración frontend
4. **Componentes Frontend**: Crear componentes Vue.js para interactividad
5. **Plantillas**: Diseñar plantillas HTML responsivas
6. **Permisos**: Definir permisos personalizados para roles de usuario

### Flujo de Trabajo de Desarrollo

```bash
# Desarrollo de características
git checkout -b feature/nuevo-seguimiento-salud
python manage.py makemigrations
python manage.py migrate
# ... desarrollar y testear ...
git commit -m "Agregar características avanzadas de seguimiento de salud"
git push origin feature/nuevo-seguimiento-salud
```

## 🤝 Contribuir

¡Damos la bienvenida a las contribuciones! Por favor sigue estas pautas:

### Para Empezar
1. **Fork** el repositorio en GitHub
2. **Clona** tu fork localmente
3. **Crea** una rama de característica: `git checkout -b feature/caracteristica-increible`
4. **Realiza** tus cambios con las pruebas apropiadas
5. **Commit** con mensajes descriptivos: `git commit -m 'Agregar característica increíble'`
6. **Push** a tu rama: `git push origin feature/caracteristica-increible`
7. **Envía** un Pull Request con descripción detallada

### Estándares de Código
- **Python**: Seguir PEP 8, usar type hints donde sea aplicable
- **JavaScript**: Usar configuración ESLint, preferir sintaxis moderna ES6+
- **Documentación**: Actualizar README.md y agregar docstrings para nuevas funciones
- **Testing**: Agregar tests para nueva funcionalidad
- **Mensajes de Commit**: Usar formato de commit convencional

### Reporte de Problemas
- Usar GitHub Issues para reportes de bugs y solicitudes de características
- Incluir pasos detallados para reproducir problemas
- Proporcionar información del sistema y logs de errores
- Etiquetar issues apropiadamente (bug, mejora, documentación)

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para detalles.

```
Copyright (c) 2024 Proyecto Gatinos

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y archivos de documentación asociados (el "Software"), para tratar
el Software sin restricción, incluyendo sin limitación los derechos
de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender
copias del Software...
```

## 🙏 Agradecimientos

- **Comunidad Django** - Por el robusto framework web
- **Equipo Vue.js** - Por la biblioteca frontend reactiva
- **Contribuidores Open Source** - Todas las increíbles bibliotecas de las que dependemos
- **Voluntarios de Colonias Felinas** - Los verdaderos héroes que inspiraron este proyecto
- **Profesionales Veterinarios** - Por la orientación en los requisitos de seguimiento de salud

## 📞 Soporte y Comunidad

### Obtener Ayuda
- **📚 Documentación**: Consulta este README y la documentación en línea del código
- **🐛 Reportes de Bugs**: Abre un issue en GitHub con información detallada
- **💡 Solicitudes de Características**: Usa GitHub Issues con la etiqueta "mejora"
- **💬 Discusiones**: Únete a nuestras discusiones comunitarias para preguntas generales

### Información de Contacto
- **Mantenedor del Proyecto**: [Tu Nombre](mailto:tu-email@ejemplo.com)
- **GitHub Issues**: [Reportar Problemas](https://github.com/tu-org/gatinos/issues)
- **Foro Comunitario**: [Unirse a Discusiones](https://github.com/tu-org/gatinos/discussions)

---

**Hecho con ❤️ para los voluntarios de colonias felinas y los gatos que cuidan.**

*"A los ojos de un gato, todas las cosas pertenecen a los gatos." - Desconocido*
