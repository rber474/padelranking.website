from flask import Blueprint

blueprint = Blueprint(
    'users',
    __name__,
    url_prefix='/users',
    template_folder='templates',
    static_folder='static'
)