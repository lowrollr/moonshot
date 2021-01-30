import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

bp = Blueprint('coin', __name__, url_prefix='/coin')

@bp.route('/{COIN}', methods=('GET'))
def dashboard():
    return render_template('main_dash.html')