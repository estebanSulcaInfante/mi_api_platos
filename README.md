# Mi API de Platos (Flask + PostgreSQL + JWT)

Este repositorio contiene un backend en Flask que expone un CRUD de **Categorías** y **Platos**, protegido con autenticación JWT para administradores.  

## Tecnologías
- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- Flask-JWT-Extended
- PostgreSQL (local y Heroku Postgres)
- Gunicorn (para producción en Heroku)

## Organización de archivos

```
mi_api_platos/
├── app.py           # Código principal de Flask
├── config.py        # Configuración (DB, JWT, SECRET_KEY)
├── models.py        # Modelos SQLAlchemy: Administrador, Categoria, Plato
├── migrations/      # Carpeta de migraciones Alembic
├── requirements.txt # Dependencias (pip freeze)
├── Procfile         # Para deploy en Heroku
├── .env             # Variables de entorno en local (no incluido en Git)
├── .gitignore
└── README.md
```

## Instalación local

1. Clonar el repositorio:
   ```bash
   git clone <URL_DE_TU_REPO>
   cd mi_api_platos
   ```

2. Crear y activar entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\Activate.ps1     # Windows PowerShell
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Crear un archivo `.env` (NO subirlo a Git) con al menos:
   ```
   DATABASE_URL=postgresql://usuario:password@localhost:5432/mi_api_platos_db
   SECRET_KEY=una_clave_muy_secreta_local
   FLASK_ENV=development
   ```

5. Inicializar migraciones y crear tablas:
   ```bash
   flask db init
   flask db migrate -m "Esquema inicial"
   flask db upgrade
   ```

6. Ejecutar la aplicación en modo debug:
   ```bash
   flask run
   ```
   Accede a `http://127.0.0.1:5000`.

## Uso de la API

1. **Registrar administrador**  
   `POST /api/register`  
   Body JSON:
   ```json
   {
     "nombre": "Angie",
     "email": "angie@ejemplo.com",
     "password": "secret123"
   }
   ```

2. **Login**  
   `POST /api/login`  
   Body JSON:
   ```json
   {
     "email": "angie@ejemplo.com",
     "password": "secret123"
   }
   ```
   → Devuelve `{ "access_token": "..." }`.

3. A partir de aquí, todas las rutas CRUD requieren JWT en el header:
   ```
   Authorization: Bearer <access_token>
   ```

   - `GET /api/categorias`  
   - `POST /api/categorias`  
   - `PUT /api/categorias/<id>`  
   - `DELETE /api/categorias/<id>`  

   - `GET /api/platos`  
   - `POST /api/platos`  
   - `PUT /api/platos/<id>`  
   - `DELETE /api/platos/<id>`

Los detalles de cada endpoint están en el código fuente (`app.py`).

## Desplegar en Heroku

1. Crea una app en Heroku:
   ```bash
   heroku create nombre-de-tu-app
   heroku addons:create heroku-postgresql:hobby-dev
   ```
   Esto provisiona una base de datos Postgres y configura `DATABASE_URL` automáticamente.

2. Agrega tu `SECRET_KEY` en Heroku:
   ```bash
   heroku config:set SECRET_KEY="una_clave_muy_secreta_en_produccion"
   heroku config:set FLASK_ENV=production
   ```

3. Asegúrate de tener un `Procfile` con:
   ```
   web: gunicorn app:create_app()
   ```

4. Empuja a Heroku:
   ```bash
   git push heroku main
   ```

5. Corre migraciones en producción:
   ```bash
   heroku run flask db upgrade
   ```

6. Tu API estará disponible en:
   ```
   https://<nombre-de-tu-app>.herokuapp.com/api/…
   ```
