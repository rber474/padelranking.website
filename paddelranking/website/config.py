import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'paddelranking.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class FlaskUploadConfig(object):
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOADED_PHOTOS_DEST = 'paddelranking/website/users/static/uploads/photos'
    UPLOADED_PORTRAITS_DEST = 'paddelranking/website/users/static/uploads/portraits'


class FlaskResizeConfig(object):
    RESIZE_URL = 'http://localhost:5000/users/static/uploads'
    RESIZE_ROOT = 'paddelranking/website/users/static/uploads'