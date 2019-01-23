from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


bp = Blueprint('front-page', __name__)


@bp.route('/')
@bp.route('/index')
def index():

    return render_template('index.html', title='Welcome to your paddel app',)