# blueprints/galeria.py

from flask import Blueprint, request, jsonify
from models import Categoria
from sqlalchemy.orm import joinedload
from sqlalchemy import func

galeria_bp = Blueprint('galeria', __name__, url_prefix='/api/galeria')

@galeria_bp.route('', methods=['GET'])
def obtener_galeria():
    """
    GET /api/galeria
    Parámetros opcionales:
      - page (int): número de página (por defecto 1)
      - per_page (int): ítems por página (por defecto 10)
      - search (str): texto para filtrar nombre o descripción de categoría
    """
    # 1) Leer query params
    page     = request.args.get('page',     default=1,  type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    search   = request.args.get('search',   default=None, type=str)

    # 2) Base query con joinedload para traer platos en la misma consulta
    query = Categoria.query.options(joinedload(Categoria.platos))

    # 3) Si vienen términos de búsqueda, filtrar por nombre o descripción
    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Categoria.nombre).like(pattern) |
            func.lower(Categoria.descripcion).like(pattern)
        )

    # 4) Paginación (error_out=False para no 404 si la página está vacía)
    pag = query.order_by(Categoria.id_categoria) \
               .paginate(page=page, per_page=per_page, error_out=False)

    # 5) Construir payload
    categorias = []
    for cat in pag.items:
        categorias.append({
            "id_categoria": cat.id_categoria,
            "nombre":       cat.nombre,
            "descripcion":  cat.descripcion,
            "platos": [
                # usamos el as_dict() de tu modelo Plato
                p.as_dict() for p in cat.platos
            ]
        })

    return jsonify({
        "page":       pag.page,
        "per_page":   pag.per_page,
        "total":      pag.total,
        "categorias": categorias
    }), 200
