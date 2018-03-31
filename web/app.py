#!/usr/bin/env python3

from flask import Flask, render_template, send_file, jsonify
from datetime import datetime, timedelta
app = Flask(__name__)

PREDICTION_HORIZON = 34  # we can download 34 images in the future (thus 34*5 min)


def get_possible_instants():
    now = datetime.utcnow()
    delta = timedelta(minutes=(- now.minute % 5), seconds=now.second, microseconds=now.microsecond)
    frame_time = now + delta

    return [frame_time + i * timedelta(minutes=5) for i in range(PREDICTION_HORIZON)]


@app.route("/")
def hello():
    return render_template('home.html', name=1)


@app.route("/api/available_images.json")
def available_images():
    instants = get_possible_instants()

    def instant_to_str(instant):
        return instant.strftime("%Y%m%d%H%M")
    return jsonify([(x, instant_to_str(x)) for x in instants])


@app.route("/img.png")
def img():
    return send_file("../red.png", mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
