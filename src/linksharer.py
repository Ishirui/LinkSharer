"""Basic hello-world example app"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    """Default route: returns a 'hello-world' HTML document"""
    return "<p>Hello, World!</p>"
