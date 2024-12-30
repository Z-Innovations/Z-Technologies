from flask import Flask, request, redirect, url_for, render_template
from markupsafe import escape
from _secrets import SECRET_KEY
from auth import MyLoginManager
from flask_login import current_user, login_user, login_required, logout_user
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.secret_key = SECRET_KEY

mgr = MyLoginManager(app)
User = mgr.User

app.register_blueprint(mgr.bp)

@app.route("/")
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