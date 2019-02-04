from flask import current_app
import babel

@current_app.template_filter('datetime')
def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d, MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd/MM/y HH:mm"
    elif format == 'short':
        format="dd/MM/y HH:mm"
    return babel.dates.format_datetime(value, format)

