import csv
import urllib.request

from flask import redirect, render_template, request, session, url_for
from functools import wraps

def page_error(error_text=""):
    """Renders message as a page_error to user."""
    
    return render_template("error.html", error=error_text)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function