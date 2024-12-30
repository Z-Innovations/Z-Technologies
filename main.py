import subprocess
from flask import Flask, request, redirect, url_for, render_template
from markupsafe import escape
from auth import MyLoginManager
from flask_login import current_user, login_required
import json

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

@app.route('/api')
@login_required
def api():
    return json.dumps({
        'name': current_user.name,
        'discriminator': current_user.id,
    })

# @mgr.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized', 401

@app.route('/__update')
def update():
    p = subprocess.run(('git', '-C', REPO_LOCATION, 'pull'), capture_output=True)
    if p.returncode == 0:
        exit()
    if not app.debug:
        return 'error'
    return f'error {p.returncode} {p.stdout.decode()} 0 {p.stderr.decode()}'