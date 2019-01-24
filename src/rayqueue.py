#!/usr/bin/env python

_author__  = 'Oliver Cordes'

__version__ = '0.0.1'


import os

from flask import Flask, request, render_template, send_from_directory


# app definitions for Flask

app = Flask(__name__)



APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)

    return render_template("complete.html")


# test this file
if __name__ == "__main__":
    app.run(port=4555, debug=True)
