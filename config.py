# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # URI de la base de datos (Heroku en producción o local.db en desarrollo)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'local.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clave secreta para Flask y para JWT
    SECRET_KEY = os.environ.get("SECRET_KEY", "1234")
    JWT_SECRET_KEY = SECRET_KEY  # Usaremos la misma clave para firmar tokens JWT
