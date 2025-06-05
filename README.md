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

# Uso de la API de Platos

Esta API en Flask expone un CRUD de **Categorías** y **Platos**, protegido con autenticación JWT para administradores.

## Base URL
```
https://mi-api-platos-68a096918f34.herokuapp.com
```

---

## 1. Rutas Públicas

### 1.1. Registro de Administrador
- **Método:** `POST`
- **Endpoint:** `/api/register`
- **Descripción:** Crea un nuevo administrador.
- **Body (JSON):**
  ```json
  {
    "nombre": "Juan",
    "email": "juan@ejemplo.com",
    "password": "abc123"
  }
  ```
- **Respuestas:**
  - `201 Created`
    ```json
    { "mensaje": "Administrador creado exitosamente" }
    ```
  - `400 Bad Request`
    ```json
    { "error": "Faltan campos obligatorios: 'nombre', 'email' o 'password'" }
    ```
  - `409 Conflict`
    ```json
    { "error": "Ya existe un administrador con ese email" }
    ```

### 1.2. Login de Administrador
- **Método:** `POST`
- **Endpoint:** `/api/login`
- **Descripción:** Valida credenciales y devuelve un JWT (`access_token`).
- **Body (JSON):**
  ```json
  {
    "email": "juan@ejemplo.com",
    "password": "abc123"
  }
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "access_token": "<JWT_TOKEN>",
      "admin": {
        "id_administrador": "1",
        "nombre": "Juan",
        "email": "juan@ejemplo.com",
        "fecha_registro": "2025-06-07T12:00:00.123456"
      }
    }
    ```
  - `400 Bad Request`
    ```json
    { "error": "Debes proporcionar 'email' y 'password'" }
    ```
  - `401 Unauthorized`
    ```json
    { "error": "Email o contraseña inválidos" }
    ```

> **Nota:** el JWT (`access_token`) expira por defecto a los 24 horas. Es obligatorio incluirlo en el header `Authorization` de todas las rutas protegidas.

---

## 2. Autenticación

Todas las rutas que siguen requieren el header HTTP:
```
Authorization: Bearer <JWT_TOKEN>
```
Reemplace `<JWT_TOKEN>` por el valor completo de `access_token` obtenido en `/api/login`.

---

## 3. CRUD de Categorías

#### 3.1. Listar Categorías
- **Método:** `GET`
- **Endpoint:** `/api/categorias`
- **Descripción:** Devuelve todas las categorías del administrador autenticado.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id_categoria": 1,
        "nombre": "Entradas",
        "descripcion": "Aperitivos",
        "id_administrador": 1
      },
      {
        "id_categoria": 2,
        "nombre": "Platos Fuertes",
        "descripcion": "Principal",
        "id_administrador": 1
      }
    ]
    ```
  - `401 Unauthorized` (token ausente o inválido)

#### 3.2. Obtener Categoría por ID
- **Método:** `GET`
- **Endpoint:** `/api/categorias/<id_categoria>`
- **Descripción:** Devuelve la categoría `<id_categoria>` si le pertenece al admin.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "id_categoria": 1,
      "nombre": "Entradas",
      "descripcion": "Aperitivos",
      "id_administrador": 1
    }
    ```
  - `404 Not Found`
    ```json
    { "error": "Categoría no encontrada o no tienes permisos" }
    ```
  - `401 Unauthorized`

#### 3.3. Crear Categoría
- **Método:** `POST`
- **Endpoint:** `/api/categorias`
- **Descripción:** Crea una nueva categoría para el admin.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Body (JSON):**
  ```json
  {
    "nombre": "Entradas",
    "descripcion": "Aperitivos"
  }
  ```
- **Respuestas:**
  - `201 Created`
    ```json
    {
      "id_categoria": 1,
      "nombre": "Entradas",
      "descripcion": "Aperitivos",
      "id_administrador": 1
    }
    ```
  - `400 Bad Request`
    ```json
    { "error": "El campo 'nombre' es obligatorio" }
    ```
  - `409 Conflict`
    ```json
    { "error": "Ya existe una categoría con ese nombre para este administrador" }
    ```
  - `401 Unauthorized`

#### 3.4. Actualizar Categoría
- **Método:** `PUT`
- **Endpoint:** `/api/categorias/<id_categoria>`
- **Descripción:** Actualiza nombre o descripción de la categoría propia.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Body (JSON) (cualquiera de los campos):**
  ```json
  {
    "nombre": "Nuevo Nombre",
    "descripcion": "Nueva Descripción"
  }
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "id_categoria": 1,
      "nombre": "Nuevo Nombre",
      "descripcion": "Nueva Descripción",
      "id_administrador": 1
    }
    ```
  - `404 Not Found`
    ```json
    { "error": "Categoría no encontrada o sin permisos" }
    ```
  - `409 Conflict`
    ```json
    { "error": "Ya tienes otra categoría con ese nombre" }
    ```
  - `401 Unauthorized`

#### 3.5. Eliminar Categoría
- **Método:** `DELETE`
- **Endpoint:** `/api/categorias/<id_categoria>`
- **Descripción:** Elimina la categoría si no tiene platos asociados y le pertenece al admin.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    { "mensaje": "Categoría eliminada" }
    ```
  - `404 Not Found`
    ```json
    { "error": "Categoría no encontrada o sin permisos" }
    ```
  - `400 Bad Request`
    ```json
    { "error": "No puedes eliminar: existen platos en esta categoría" }
    ```
  - `401 Unauthorized`

---

## 4. CRUD de Platos

#### 4.1. Listar Platos
- **Método:** `GET`
- **Endpoint:** `/api/platos`
- **Descripción:** Devuelve todos los platos del admin autenticado.  
  Se puede filtrar por categoría propia con query param `?id_categoria=<id>`.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Query params (opcional):**
  ```
  id_categoria=2
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    [
      {
        "id_plato": 1,
        "nombre": "Ceviche de pescado",
        "descripcion": "Pescado fresco con limón, cebolla y ají.",
        "foto_url": "https://mi-bucket/ceviche.jpg",
        "precio": "35.50",
        "tiempo_preparacion_min": 20,
        "porciones": 2,
        "info_nutricional": "200 kcal/porción",
        "fecha_creacion": "2025-06-07T12:15:00.123456",
        "id_categoria": 1,
        "id_administrador": 1
      },
      {
        "id_plato": 2,
        "nombre": "Lomo Saltado",
        "descripcion": "Carne salteada con verduras y papas fritas",
        "foto_url": "https://mi-bucket/lomo.jpg",
        "precio": "40.00",
        "tiempo_preparacion_min": 25,
        "porciones": 2,
        "info_nutricional": "450 kcal/porción",
        "fecha_creacion": "2025-06-07T12:20:00.123456",
        "id_categoria": 2,
        "id_administrador": 1
      }
    ]
    ```
  - `404 Not Found` (si se filtra por `id_categoria` inexistente o que no le pertenece)
  - `401 Unauthorized`

#### 4.2. Obtener Plato por ID
- **Método:** `GET`
- **Endpoint:** `/api/platos/<id_plato>`
- **Descripción:** Devuelve el plato `<id_plato>` si le pertenece al admin autenticado.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "id_plato": 1,
      "nombre": "Ceviche de pescado",
      "descripcion": "Pescado fresco con limón, cebolla y ají.",
      "foto_url": "https://mi-bucket/ceviche.jpg",
      "precio": "35.50",
      "tiempo_preparacion_min": 20,
      "porciones": 2,
      "info_nutricional": "200 kcal/porción",
      "fecha_creacion": "2025-06-07T12:15:00.123456",
      "id_categoria": 1,
      "id_administrador": 1
    }
    ```
  - `404 Not Found`
    ```json
    { "error": "Plato no encontrado o sin permisos" }
    ```
  - `401 Unauthorized`

#### 4.3. Crear Plato
- **Método:** `POST`
- **Endpoint:** `/api/platos`
- **Descripción:** Crea un nuevo plato para el admin autenticado.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Body (JSON) mínimo**:
  ```json
  {
    "nombre": "Ceviche de pescado",
    "foto_url": "https://mi-bucket/ceviche.jpg",
    "id_categoria": 1
  }
  ```
- **Body (JSON) opcional** (además de lo anterior):
  ```json
  {
    "descripcion": "Pescado fresco con limón, cebolla y ají.",
    "precio": 35.50,
    "tiempo_preparacion_min": 20,
    "porciones": 2,
    "info_nutricional": "200 kcal/porción"
  }
  ```
- **Respuestas:**
  - `201 Created`
    ```json
    {
      "id_plato": 1,
      "nombre": "Ceviche de pescado",
      "descripcion": "Pescado fresco con limón, cebolla y ají.",
      "foto_url": "https://mi-bucket/ceviche.jpg",
      "precio": "35.50",
      "tiempo_preparacion_min": 20,
      "porciones": 2,
      "info_nutricional": "200 kcal/porción",
      "fecha_creacion": "2025-06-07T12:15:00.123456",
      "id_categoria": 1,
      "id_administrador": 1
    }
    ```
  - `400 Bad Request`
    ```json
    { "error": "Debes enviar 'nombre', 'foto_url' e 'id_categoria'" }
    ```
  - `404 Not Found`
    ```json
    { "error": "Categoría no encontrada o sin permisos" }
    ```
  - `401 Unauthorized`

#### 4.4. Actualizar Plato
- **Método:** `PUT`
- **Endpoint:** `/api/platos/<id_plato>`
- **Descripción:** Actualiza campos de un plato existente, si le pertenece al admin.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Body (JSON)** (cualquiera de estos campos):
  ```json
  {
    "nombre": "Nuevo Nombre",
    "descripcion": "Nueva descripción",
    "foto_url": "https://mi-bucket/nueva-foto.jpg",
    "precio": 38.00,
    "tiempo_preparacion_min": 18,
    "porciones": 3,
    "info_nutricional": "210 kcal/porción",
    "id_categoria": 2
  }
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    {
      "id_plato": 1,
      "nombre": "Nuevo Nombre",
      "descripcion": "Nueva descripción",
      "foto_url": "https://mi-bucket/nueva-foto.jpg",
      "precio": "38.00",
      "tiempo_preparacion_min": 18,
      "porciones": 3,
      "info_nutricional": "210 kcal/porción",
      "fecha_creacion": "2025-06-07T12:15:00.123456",
      "id_categoria": 2,
      "id_administrador": 1
    }
    ```
  - `404 Not Found`
    ```json
    { "error": "Plato no encontrado o sin permisos" }
    ```
  - `404 Not Found` (si `id_categoria` nuevo no existe o no le pertenece)
    ```json
    { "error": "La nueva categoría no existe o no te pertenece" }
    ```
  - `401 Unauthorized`

#### 4.5. Eliminar Plato
- **Método:** `DELETE`
- **Endpoint:** `/api/platos/<id_plato>`
- **Descripción:** Elimina un plato si le pertenece al admin autenticado.
- **Header:**  
  ```
  Authorization: Bearer <JWT_TOKEN>
  ```
- **Respuestas:**
  - `200 OK`
    ```json
    { "mensaje": "Plato eliminado" }
    ```
  - `404 Not Found`
    ```json
    { "error": "Plato no encontrado o sin permisos" }
    ```
  - `401 Unauthorized`

---

## 5. Ejemplo de Flujo Completo

1. **Registro**  
   ```bash
   curl -X POST https://mi-api-platos-68a096918f34.herokuapp.com/api/register      -H "Content-Type: application/json"      -d '{
           "nombre": "Juan",
           "email": "juan@ejemplo.com",
           "password": "abc123"
         }'
   ```
   → `201 Created`: `{ "mensaje": "Administrador creado exitosamente" }`

2. **Login**  
   ```bash
   curl -X POST https://mi-api-platos-68a096918f34.herokuapp.com/api/login      -H "Content-Type: application/json"      -d '{
           "email": "juan@ejemplo.com",
           "password": "abc123"
         }'
   ```
   → `200 OK`:
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
     "admin": {
       "id_administrador": "1",
       "nombre": "Juan",
       "email": "juan@ejemplo.com",
       "fecha_registro": "2025-06-07T12:00:00.123456"
     }
   }
   ```
   Guarda `<JWT_TOKEN>`.

3. **Crear Categoría**  
   ```bash
   curl -X POST https://mi-api-platos-68a096918f34.herokuapp.com/api/categorias      -H "Authorization: Bearer <JWT_TOKEN>"      -H "Content-Type: application/json"      -d '{
           "nombre": "Entradas",
           "descripcion": "Aperitivos"
         }'
   ```
   → `201 Created`:
   ```json
   {
     "id_categoria": 1,
     "nombre": "Entradas",
     "descripcion": "Aperitivos",
     "id_administrador": 1
   }
   ```

4. **Crear Plato**  
   ```bash
   curl -X POST https://mi-api-platos-68a096918f34.herokuapp.com/api/platos      -H "Authorization: Bearer <JWT_TOKEN>"      -H "Content-Type: application/json"      -d '{
           "nombre": "Ceviche de pescado",
           "descripcion": "Pescado fresco con limón, cebolla y ají.",
           "foto_url": "https://mi-bucket/ceviche.jpg",
           "precio": 35.50,
           "tiempo_preparacion_min": 20,
           "porciones": 2,
           "info_nutricional": "200 kcal/porción",
           "id_categoria": 1
         }'
   ```
   → `201 Created`:
   ```json
   {
     "id_plato": 1,
     "nombre": "Ceviche de pescado",
     "descripcion": "Pescado fresco con limón, cebolla y ají.",
     "foto_url": "https://mi-bucket/ceviche.jpg",
     "precio": "35.50",
     "tiempo_preparacion_min": 20,
     "porciones": 2,
     "info_nutricional": "200 kcal/porción",
     "fecha_creacion": "2025-06-07T12:15:00.123456",
     "id_categoria": 1,
     "id_administrador": 1
   }
   ```

5. **Listar Platos**  
   ```bash
   curl -H "Authorization: Bearer <JWT_TOKEN>"         https://mi-api-platos-68a096918f34.herokuapp.com/api/platos
   ```
   → `200 OK` con lista de todos los platos del admin.

6. **Actualizar Plato**  
   ```bash
   curl -X PUT https://mi-api-platos-68a096918f34.herokuapp.com/api/platos/1      -H "Authorization: Bearer <JWT_TOKEN>"      -H "Content-Type: application/json"      -d '{
           "precio": 38.00,
           "porciones": 3
         }'
   ```
   → `200 OK` con objeto del plato actualizado.

7. **Eliminar Plato**  
   ```bash
   curl -X DELETE https://mi-api-platos-68a096918f34.herokuapp.com/api/platos/1      -H "Authorization: Bearer <JWT_TOKEN>"
   ```
   → `200 OK`: `{ "mensaje": "Plato eliminado" }`

---

## 6. Manejo de Errores Comunes

- **401 Unauthorized**  
  - No incluiste el header `Authorization` o el token expiró.  
  - Mensaje:  
    ```json
    { "msg": "Token has expired" }
    ```  
  - Solución: volver a hacer login y usar un JWT válido.

- **400 Bad Request**  
  - Faltan campos obligatorios en el body JSON.  
  - Ejemplo:  
    ```json
    { "error": "Debes enviar 'nombre', 'foto_url' e 'id_categoria'" }
    ```

- **404 Not Found**  
  - Intentas acceder o modificar un recurso (categoría/plato) que no existe o que no te pertenece.  
  - Ejemplo:  
    ```json
    { "error": "Plato no encontrado o sin permisos" }
    ```

- **409 Conflict**  
  - Tratas de crear una categoría con un nombre que ya existe para tu usuario.  
  - Ejemplo:  
    ```json
    { "error": "Ya existe una categoría con ese nombre para este administrador" }
    ```

---


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
