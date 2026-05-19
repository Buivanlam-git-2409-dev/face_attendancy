from flask import Blueprint

from backend.api.v1 import v1Blueprint


apiBlueprint = Blueprint("api", __name__, url_prefix="/api")
apiBlueprint.register_blueprint(v1Blueprint)
