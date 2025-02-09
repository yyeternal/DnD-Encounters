from flask import Blueprint
from flask_moment import Moment

main_blueprint = Blueprint('main', __name__)

from app.main import routes