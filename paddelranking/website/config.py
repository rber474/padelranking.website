import os
basedir = os.path.relpath(os.path.dirname(__file__))

class Config(object):
    LANGUAGES = {
        'en': 'English',
        'es': 'Español'
    }

class FlaskUploadConfig(object):
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOADED_PHOTOS_DEST = '{}/users/static/uploads/photos'.format(basedir)
    UPLOADED_PORTRAITS_DEST = '{}/users/static/uploads/portraits'.format(basedir)


class FlaskResizeConfig(object):
    #RESIZE_URL = 'https://rber474.pythonanywhere.com/users/static/uploads'
    RESIZE_URL = 'http://localhost:5000/users/static/uploads'
    RESIZE_ROOT = '{}/users/static/uploads'.format(basedir)

class FlaskAdminConfig(object):
    RESIZE_URL = 'http://localhost:5000/admin/static/uploads'
    RESIZE_ROOT = '{}/admin/static/uploads'.format(basedir)
    FLASK_ADMIN_SWATCH = 'lumen'