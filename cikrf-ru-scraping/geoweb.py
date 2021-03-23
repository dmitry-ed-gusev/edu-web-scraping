#!/usr/bin/env python
# coding=utf-8

"""
    Simple web application for geo module.
    Created: Gusev Dmitrii, 10.02.2017
    Modified:
"""

from flask import Flask

# flask application
app = Flask(__name__)


# route for root of web app
@app.route("/")
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(port=5000, debug=True)
