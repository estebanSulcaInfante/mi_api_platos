# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Administrador(db.Model):
    __tablename__ = "administrador"

    id_administrador = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre           = db.Column(db.String(50), nullable=False)
    email            = db.Column(db.String(100), unique=True, nullable=False)
    password_hash    = db.Column(db.String(255), nullable=False)
    fecha_registro   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relación inversa (backref) para categorías y platos
    categorias = db.relationship("Categoria", backref="administrador", lazy=True)
    platos     = db.relationship("Plato", backref="administrador", lazy=True)

    def set_password(self, password_plain: str):
        self.password_hash = generate_password_hash(password_plain)

    def check_password(self, password_plain: str) -> bool:
        return check_password_hash(self.password_hash, password_plain)

    def as_dict(self):
        return {
            "id_administrador": self.id_administrador,
            "nombre": self.nombre,
            "email": self.email,
            "fecha_registro": self.fecha_registro.isoformat()
        }


class Categoria(db.Model):
    __tablename__ = "categoria"

    id_categoria     = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre           = db.Column(db.String(30), unique=False, nullable=False)
    descripcion      = db.Column(db.String(100), nullable=True)
    id_administrador = db.Column(
        db.BigInteger,
        db.ForeignKey("administrador.id_administrador"),
        nullable=False
    )

    # Relación a Plato
    platos = db.relationship("Plato", backref="categoria", lazy=True)

    def as_dict(self):
        return {
            "id_categoria": self.id_categoria,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "id_administrador": self.id_administrador
        }


class Plato(db.Model):
    __tablename__ = "plato"

    id_plato               = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre                 = db.Column(db.String(50), nullable=False)
    descripcion            = db.Column(db.Text, nullable=True)
    foto_url               = db.Column(db.String(255), nullable=False)
    precio                 = db.Column(db.Numeric(8, 2), nullable=True)
    tiempo_preparacion_min = db.Column(db.Integer, nullable=True)
    porciones              = db.Column(db.Integer, nullable=True)
    info_nutricional       = db.Column(db.Text, nullable=True)
    fecha_creacion         = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_categoria           = db.Column(
        db.BigInteger,
        db.ForeignKey("categoria.id_categoria"),
        nullable=False
    )
    id_administrador       = db.Column(
        db.BigInteger,
        db.ForeignKey("administrador.id_administrador"),
        nullable=False
    )

    def as_dict(self):
        return {
            "id_plato": self.id_plato,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "foto_url": self.foto_url,
            "precio": str(self.precio) if self.precio is not None else None,
            "tiempo_preparacion_min": self.tiempo_preparacion_min,
            "porciones": self.porciones,
            "info_nutricional": self.info_nutricional,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "id_categoria": self.id_categoria,
            "id_administrador": self.id_administrador
        }
