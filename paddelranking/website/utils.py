from collections import deque
from itertools import islice
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

def fixtures(teams):

    if len(teams) % 2:
        teams.append("Bye")

    ln = len(teams) // 2
    dq1, dq2 = deque(islice(teams, None, ln)), deque(islice(teams, ln, None))
    for _ in range(len(teams)-1):
        yield list(zip(dq1, dq2)) # list(zip.. python3
        #  pop off first deque's left element to 
        # "fix one of the competitors in the first column"
        start = dq1.popleft() 
        # rotate the others clockwise one position
        # by swapping elements 
        dq1.appendleft(dq2.popleft())
        dq2.append(dq1.pop())
        # reattach first competitor
        dq1.appendleft(start)

