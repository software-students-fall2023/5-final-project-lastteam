"""Web App"""
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """Route for home page"""
    return render_template("index.html")
