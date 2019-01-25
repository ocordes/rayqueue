from app import app


import os

from flask import request, render_template, send_from_directory, jsonify



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


@app.route('/api', methods=['POST'])
def api():
    return jsonify(username='hello',
                   email='president@whitehouse.gov',
                   id=42)
