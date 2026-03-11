from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from storage import init_db, save_run, list_runs, get_last_run
from tester.runner import run_all_tests
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

#app = Flask(__name__)

#@app.get("/")
#def consignes():
#     return render_template('consignes.html')

#if __name__ == "__main__":
    # utile en local uniquement
#    app.run(host="0.0.0.0", port=5000, debug=True)





app = Flask(__name__)
init_db()


@app.route("/")
def home():
    return jsonify({
        "message": "API Test Dashboard",
        "routes": ["/run", "/dashboard", "/health"]
    })


@app.route("/run")
def run():
    run_data = run_all_tests()
    save_run(run_data)
    return jsonify(run_data)


@app.route("/dashboard")
def dashboard():
    runs = list_runs(limit=20)
    last_run = get_last_run()
    return render_template("dashboard.html", runs=runs, last_run=last_run)


@app.route("/health")
def health():
    last_run = get_last_run()
    if not last_run:
        return jsonify({"status": "unknown", "message": "No run yet"}), 200

    ok = last_run["failed"] == 0
    return jsonify({
        "status": "healthy" if ok else "degraded",
        "last_timestamp": last_run["timestamp"],
        "availability": last_run["availability"],
        "error_rate": last_run["error_rate"]
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
