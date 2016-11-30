import csv
import urllib.request

from flask import redirect, render_template, request, session, url_for
from functools import wraps

def page_error(error_text=""):
    """Renders message as a page_error to user."""
    
    return render_template("error.html", error=error_text)
