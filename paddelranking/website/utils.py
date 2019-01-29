
from functools import wraps
from flask import flash, g, request, redirect, url_for, current_app
from flask_login import current_user

from paddelranking.website import babel

def is_current_user(f):
    """ check if current user is trying to access othen panel that his """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.username != kwargs.get('username'):
            flash('You cannot access a control panel other than yours', 'error')
            return redirect(url_for('users.user', username=current_user.username))
        return f(*args, **kwargs)
    return decorated_function

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])