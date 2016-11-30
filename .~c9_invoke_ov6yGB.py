import re
from flask import Flask, jsonify, render_template, request, url_for
from flask_jsglue import JSGlue
import json

import cs50

# configure application
app = Flask(__name__)
JSGlue(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
        
@app.route("/")
def index():
    return render_template("board.html")