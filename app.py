# app.py

import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_cors import CORS
from config import Config
from models import db, Administrador, Categoria, Plato

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    # ─── Habilitar CORS global para cualquier origen ───
    # Con esto, cualquier petición HTTP (GET, POST, PUT, DELETE, etc.)
    # desde cualquier dominio (Origin: *) podrá llamar a tus endpoints /api/*
    CORS(app, origins="*")

    
    # --------------------------
    # RUTAS PÚBLICAS: Registro / Login
    # --------------------------

    @app.route("/api/register", methods=["POST"])
    def register():
        """
        Registro de un nuevo administrador.
        Body JSON: { "nombre": "Juan", "email": "juan@ejemplo.com", "password": "abc123" }
        """
        data = request.get_json() or {}
        nombre = data.get("nombre")
        email = data.get("email")
        password = data.get("password")

        if not nombre or not email or not password:
            return jsonify({"error": "Faltan campos obligatorios: 'nombre', 'email' o 'password'"}), 400

        # Verificar que no exista ya ese email
        if Administrador.query.filter_by(email=email).first():
            return jsonify({"error": "Ya existe un administrador con ese email"}), 409

        admin = Administrador(nombre=nombre, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        return jsonify({"mensaje": "Administrador creado exitosamente"}), 201

    @app.route("/api/login", methods=["POST"])
    def login():
        """
        Login de administrador. Devuelve un access_token JWT.
        Body JSON: { "email": "juan@ejemplo.com", "password": "abc123" }
        """
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Debes proporcionar 'email' y 'password'"}), 400

        admin = Administrador.query.filter_by(email=email).first()
        if not admin or not admin.check_password(password):
            return jsonify({"error": "Email o contraseña inválidos"}), 401

        # Creamos el token con identidad = id_administrador
        access_token = create_access_token(identity=str(admin.id_administrador))
        return jsonify({
            "access_token": access_token,
            "admin": admin.as_dict()
        }), 200

    # --------------------------
    # RUTAS PROTEGIDAS (solo administradores autenticados)
    # --------------------------

    # ─── CRUD para Categoría ───

    @app.route("/api/categorias", methods=["GET"])
    @jwt_required()
    def listar_categorias():
        """
        Lista todas las categorías del administrador autenticado.
        """
        # get_jwt_identity() devuelve el id_administrador del token válido
        admin_id = get_jwt_identity()

        categorias = Categoria.query.filter_by(id_administrador=admin_id).all()
        return jsonify([c.as_dict() for c in categorias]), 200

    @app.route("/api/categorias/<int:id_categoria>", methods=["GET"])
    @jwt_required()
    def obtener_categoria(id_categoria):
        """
        Devuelve datos de una categoría específica, pero sólo si pertenece al admin que hace la petición.
        """
        admin_id = get_jwt_identity()
        cat = Categoria.query.filter_by(id_categoria=id_categoria, id_administrador=admin_id).first()
        if not cat:
            return jsonify({"error": "Categoría no encontrada o no tienes permisos"}), 404
        return jsonify(cat.as_dict()), 200

    @app.route("/api/categorias", methods=["POST"])
    @jwt_required()
    def crear_categoria():
        """
        Crea una nueva categoría para el admin autenticado.
        Body JSON: { "nombre": "Entradas", "descripcion": "Aperitivos" }
        """
        admin_id = get_jwt_identity()
        data = request.get_json() or {}
        nombre = data.get("nombre")
        descripcion = data.get("descripcion")

        if not nombre:
            return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400

        # Verificar que esa misma categoría no exista para este administrador
        existe = Categoria.query.filter_by(nombre=nombre, id_administrador=admin_id).first()
        if existe:
            return jsonify({"error": "Ya existe una categoría con ese nombre para este administrador"}), 409

        cat = Categoria(nombre=nombre, descripcion=descripcion, id_administrador=admin_id)
        db.session.add(cat)
        db.session.commit()
        return jsonify(cat.as_dict()), 201

    @app.route("/api/categorias/<int:id_categoria>", methods=["PUT"])
    @jwt_required()
    def actualizar_categoria(id_categoria):
        """
        Actualiza nombre/descr de una categoría propia.
        Body JSON puede contener: { "nombre": "Nuevo nombre", "descripcion": "Nueva desc" }
        """
        admin_id = get_jwt_identity()
        cat = Categoria.query.filter_by(id_categoria=id_categoria, id_administrador=admin_id).first()
        if not cat:
            return jsonify({"error": "Categoría no encontrada o sin permisos"}), 404

        data = request.get_json() or {}
        if "nombre" in data:
            nuevo_nombre = data["nombre"]
            # Verificar conflicto de nombre para este administrador
            conflicto = Categoria.query.filter(
                Categoria.nombre == nuevo_nombre,
                Categoria.id_administrador == admin_id,
                Categoria.id_categoria != id_categoria
            ).first()
            if conflicto:
                return jsonify({"error": "Ya tienes otra categoría con ese nombre"}), 409
            cat.nombre = nuevo_nombre

        if "descripcion" in data:
            cat.descripcion = data["descripcion"]

        db.session.commit()
        return jsonify(cat.as_dict()), 200

    @app.route("/api/categorias/<int:id_categoria>", methods=["DELETE"])
    @jwt_required()
    def eliminar_categoria(id_categoria):
        """
        Elimina una categoría siempre que no tenga platos asociados y pertenezca al admin.
        """
        admin_id = get_jwt_identity()
        cat = Categoria.query.filter_by(id_categoria=id_categoria, id_administrador=admin_id).first()
        if not cat:
            return jsonify({"error": "Categoría no encontrada o sin permisos"}), 404

        # Verificar si hay platos asociados
        if Plato.query.filter_by(id_categoria=id_categoria).first():
            return jsonify({"error": "No puedes eliminar: existen platos en esta categoría"}), 400

        db.session.delete(cat)
        db.session.commit()
        return jsonify({"mensaje": "Categoría eliminada"}), 200

    # ─── CRUD para Plato ───

    @app.route("/api/platos", methods=["GET"])
    @jwt_required()
    def listar_platos():
        """
        Lista todos los platos del administrador autenticado.
        Permite filtrar opcionalmente por categoría propia: ?id_categoria=2
        """
        admin_id = get_jwt_identity()
        id_cat = request.args.get("id_categoria", type=int)

        query = Plato.query.filter_by(id_administrador=admin_id)
        if id_cat:
            # Asegurarse que la categoría pertenece a este administrador
            cat_propia = Categoria.query.filter_by(id_categoria=id_cat, id_administrador=admin_id).first()
            if not cat_propia:
                return jsonify({"error": "Categoría no encontrada o sin permisos"}), 404
            query = query.filter_by(id_categoria=id_cat)

        platos = query.all()
        return jsonify([p.as_dict() for p in platos]), 200

    @app.route("/api/platos/<int:id_plato>", methods=["GET"])
    @jwt_required()
    def obtener_plato(id_plato):
        """
        Devuelve datos de un plato determinado, si pertenece al admin autenticado.
        """
        admin_id = get_jwt_identity()
        plato = Plato.query.filter_by(id_plato=id_plato, id_administrador=admin_id).first()
        if not plato:
            return jsonify({"error": "Plato no encontrado o sin permisos"}), 404
        return jsonify(plato.as_dict()), 200

    @app.route("/api/platos", methods=["POST"])
    @jwt_required()
    def crear_plato():
        """
        Crea un nuevo plato para el admin autenticado.
        Body JSON mínimo:
        {
          "nombre": "Ceviche de pescado",
          "foto_url": "https://.../ceviche.jpg",
          "id_categoria": 3
        }
        Otros campos opcionales: descripcion, precio, tiempo_preparacion_min, porciones, info_nutricional.
        """
        admin_id = get_jwt_identity()
        data = request.get_json() or {}

        nombre   = data.get("nombre")
        foto_url = data.get("foto_url")
        id_cat   = data.get("id_categoria")

        if not nombre or not foto_url or not id_cat:
            return jsonify({"error": "Debes enviar 'nombre', 'foto_url' e 'id_categoria'"}), 400

        # La categoría debe existir y ser propiedad del admin
        categoria = Categoria.query.filter_by(id_categoria=id_cat, id_administrador=admin_id).first()
        if not categoria:
            return jsonify({"error": "Categoría no encontrada o sin permisos"}), 404

        plato = Plato(
            nombre=nombre,
            descripcion=data.get("descripcion"),
            foto_url=foto_url,
            precio=data.get("precio"),
            tiempo_preparacion_min=data.get("tiempo_preparacion_min"),
            porciones=data.get("porciones"),
            info_nutricional=data.get("info_nutricional"),
            id_categoria=id_cat,
            id_administrador=admin_id
        )
        db.session.add(plato)
        db.session.commit()
        return jsonify(plato.as_dict()), 201

    @app.route("/api/platos/<int:id_plato>", methods=["PUT"])
    @jwt_required()
    def actualizar_plato(id_plato):
        """
        Actualiza un plato existente (si pertenece al admin). Sólo los campos que envíes en JSON.
        """
        admin_id = get_jwt_identity()
        plato = Plato.query.filter_by(id_plato=id_plato, id_administrador=admin_id).first()
        if not plato:
            return jsonify({"error": "Plato no encontrado o sin permisos"}), 404

        data = request.get_json() or {}

        if "nombre" in data:
            plato.nombre = data["nombre"]
        if "descripcion" in data:
            plato.descripcion = data["descripcion"]
        if "foto_url" in data:
            plato.foto_url = data["foto_url"]
        if "precio" in data:
            plato.precio = data["precio"]
        if "tiempo_preparacion_min" in data:
            plato.tiempo_preparacion_min = data["tiempo_preparacion_min"]
        if "porciones" in data:
            plato.porciones = data["porciones"]
        if "info_nutricional" in data:
            plato.info_nutricional = data["info_nutricional"]
        if "id_categoria" in data:
            nueva_cat = Categoria.query.filter_by(
                id_categoria=data["id_categoria"],
                id_administrador=admin_id
            ).first()
            if not nueva_cat:
                return jsonify({"error": "La nueva categoría no existe o no te pertenece"}), 404
            plato.id_categoria = data["id_categoria"]

        db.session.commit()
        return jsonify(plato.as_dict()), 200

    @app.route("/api/platos/<int:id_plato>", methods=["DELETE"])
    @jwt_required()
    def eliminar_plato(id_plato):
        """
        Elimina un plato propio.
        """
        admin_id = get_jwt_identity()
        plato = Plato.query.filter_by(id_plato=id_plato, id_administrador=admin_id).first()
        if not plato:
            return jsonify({"error": "Plato no encontrado o sin permisos"}), 404

        db.session.delete(plato)
        db.session.commit()
        return jsonify({"mensaje": "Plato eliminado"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
