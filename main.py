from pathlib import Path
import subprocess
import time, os
from flask import Flask, request, redirect, url_for, render_template
from markupsafe import escape
from auth import MyLoginManager
from flask_login import current_user, login_required
import json
from threading import Thread

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

REPO_LOCATION = '/var/www/Z-Technologies/Z-Technologies'

try:
    from _secrets import SECRET_KEY
    app.secret_key = SECRET_KEY
except: pass

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
    return json.dumps({
        'name': current_user.name,
        'discriminator': current_user.id,
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
    pull_in_progress = True
    p = subprocess.run(('git', '-C', REPO_LOCATION, 'pull'), capture_output=True)
    if p.returncode == 0:
        p = subprocess.run((Path(REPO_LOCATION).parent / '.venv/bin/flask', '--app', Path(REPO_LOCATION) / 'main', 'db', 'upgrade'), capture_output=True)
        if p.returncode == 0:
            def f():
                global pull_in_progress
                time.sleep(2)
                pull_in_progress = False
                reload()
                
            Thread(target=f).start()
            print(f"Exiting... {p.returncode}!!{p.stdout.decode()}!!{p.stderr.decode()}")
            return 'should be OK'
    print(f'error {p.returncode}!!{p.stdout.decode()}!!{p.stderr.decode()}')
    pull_in_progress = False
    if not app.debug:
        return 'error'
    return f'error {p.returncode}!!{p.stdout.decode()}!!{p.stderr.decode()}'

@app.route('/__migrate')
def migrate():
    global migrate_in_progress
    if migrate_in_progress:
        return 'already in progress'
    migrate_in_progress = True
    p = subprocess.run((Path(REPO_LOCATION).parent / '.venv/bin/flask', '--app', Path(REPO_LOCATION) / 'main', 'db', 'upgrade'), capture_output=True)
    if p.returncode == 0:
        def f():
            global migrate_in_progress
            time.sleep(2)
            migrate_in_progress = False
            reload()

        Thread(target=f).start()
        print(f"Exiting... {p.returncode}!!{p.stdout.decode()}!!{p.stderr.decode()}")
        return 'should be OK'
    migrate_in_progress = False
    if not app.debug:
        return 'error'
    return f'error {p.returncode}!!{p.stdout.decode()}!!{p.stderr.decode()}'

@app.route('/__reload')
def reload():
    #os._exit(0)
    subprocess.run(('systemctl', 'restart', 'z-tech'))
    return "<h1>something's wrong</h1>\n\ndid not restart?\n\nrestart pending?"