from flask import Blueprint

timetable_bp = Blueprint('timetable', __name__, template_folder='templates')

from . import routes
