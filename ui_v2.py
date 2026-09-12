"""v2 UI (future redesign), served under /v2. Uses the same stats.py as v1."""
from flask import Blueprint, render_template

bp = Blueprint('v2', __name__)


@bp.route('/')
def home():
    return render_template('v2/index.html')
