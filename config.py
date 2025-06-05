# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Lee lo que haya en DATABASE_URL (Heroku) o utiliza SQLite local como fallback
    url = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'local.db')}")
    # Si la URL de Heroku empieza con "postgres://", lo cambiamos a "postgresql://"
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "mi_clave_por_defecto_muy_secreta")
    JWT_SECRET_KEY = SECRET_KEY
