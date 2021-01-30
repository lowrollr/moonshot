import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard', methods=('GET'))
def dashboard():
    return render_template('main_dash.html')


