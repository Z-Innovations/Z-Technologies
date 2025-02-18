import logging
from pathlib import Path
import subprocess
import time, os
from flask import Flask, request, redirect, url_for, render_template, jsonify
from markupsafe import escape
from auth import MyLoginManager
from flask_login import current_user, login_required
import json
from threading import Thread
from logging import FileHandler
from datetime import datetime
from uuid import uuid4

from utils import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URI')

REPO_LOCATION = os.environ.get('REPO_LOCATION')

if not app.debug and REPO_LOCATION:
    log_path = Path(REPO_LOCATION).parent / 'logs'
    log_path.mkdir(parents=True, exist_ok=True)
    log_handler = FileHandler(log_path / ("z-tech-log--"+datetime.now().strftime("%Y-%m-%d--%H-%M-%S")+f"--{uuid4()}.txt"))
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(ColorfulFormatter())
    app.logger.addHandler(log_handler)
# app.logger.critical("Log initialized")

app.secret_key = os.environ.get('SECRET_KEY')

mgr = MyLoginManager(app)
User = mgr.User

app.register_blueprint(mgr.bp)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/me')
@login_required
def protected():
    return render_template('me.html')

@app.route('/meapi')
@login_required
def api():
    return jsonify({
        'name': current_user.name,
        'id': current_user.id,
        'discriminator': current_user.discriminator,
        'credit_card': {
            'number': current_user.creditcard_number,
            'valid_till': current_user.creditcard_valid_till,
            '3_digits': current_user.creditcard_3_digits,
        },
    })

# @mgr.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized', 401

pull_in_progress = False
migrate_in_progress = False

@app.route('/__update')
def update():
    global pull_in_progress
    if pull_in_progress:
        return 'already in progress'
    if not REPO_LOCATION:
        return 'REPO_LOCATION not set'
    pull_in_progress = True
    p = subprocess.run(('git', '-C', REPO_LOCATION, 'pull'), capture_output=True)
    if p.returncode == 0:
        p1 = subprocess.run((Path(REPO_LOCATION).parent / '.venv/bin/flask', '--app', Path(REPO_LOCATION) / 'main', 'db', 'upgrade'), capture_output=True)
        if p1.returncode == 0:
            def f():
                global pull_in_progress
                time.sleep(2)
                pull_in_progress = False
                reload()

            app.logger.info(construct_debug_info('__update', p, p1))
            Thread(target=f).start()
            return 'should be OK'
        l = 'migrate'
    else:
        l = 'git pull'
    l = construct_debug_info('__update', p, p1, failed_at=l)
    app.logger.error(l)
    pull_in_progress = False
    return 'error' if app.debug else l

@app.route('/__migrate')
def migrate():
    global migrate_in_progress
    if migrate_in_progress:
        return 'already in progress'
    if not REPO_LOCATION:
        return 'REPO_LOCATION not set'
    migrate_in_progress = True
    p = subprocess.run((Path(REPO_LOCATION).parent / '.venv/bin/flask', '--app', Path(REPO_LOCATION) / 'main', 'db', 'upgrade'), capture_output=True)
    if p.returncode == 0:
        def f():
            global migrate_in_progress
            time.sleep(2)
            migrate_in_progress = False
            reload()

        app.logger.info(construct_debug_info('__migrate', p))
        Thread(target=f).start()
        return 'should be OK'
    l = construct_debug_info('__migrate', p, failed_at='migrate')
    app.logger.error(l)
    migrate_in_progress = False
    return 'error' if app.debug else l

@app.route('/__reload')
def reload():
    #os._exit(0)
    subprocess.run(('systemctl', 'restart', 'z-tech'))
    return "<h1>something's wrong</h1>\n\ndid not restart?\n\nrestart pending?"

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

if __name__ == '__main__':
   app.run(host='0.0.0.0')