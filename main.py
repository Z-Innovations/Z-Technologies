from flask import Flask, request, redirect, url_for
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

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/<name>")
# def test(name):
#     # escape() fixes stuff like <script>alert("VIRUS")</script> to be passed as the name
#     return f"Signed in as {escape(name)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='name' id='name' placeholder='name'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    name, password = request.form['name'], request.form['password']
    user = User.query.filter_by(name=name).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('protected'))

    return 'Bad login'


@app.route('/protected')
@login_required
def protected():
    return f'Logged in as: {escape(current_user.name)}#{current_user.id}'

@app.route('/api')
@login_required
def api():
    return json.dumps({
        'name': current_user.name,
        'discriminator': current_user.id,
    })

@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'

# @mgr.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized', 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    match request.method:
        case 'GET':
            return '''
                    <form action='register' method='POST'>
                        <input type='text' name='name' id='name' placeholder='Олег Данилов'/>
                        <input type='password' name='password' id='password' placeholder='password'/>
                        <input type='submit' name='submit'/>
                    </form>
                    '''
        case 'POST':
            name, password = request.form['name'], request.form['password']
            user = User.query.filter_by(name=name).first()
            if not user and name and password:
                user = User(name=name, password=generate_password_hash(password))
                mgr.db.session.add(user)
                mgr.db.session.commit()
                login_user(user)
                return redirect(url_for('protected'))

    return 'something went wrong'

@app.route('/unregister', methods=['GET', 'POST'])
@login_required
def unregister():
    match request.method:
        case 'GET':
            return '''
                    <h1>U sure?</h1>
                    <p>Enter your password to confirm</p>
                    <form action='unregister' method='POST'>
                        <input type='password' name='password' id='password' placeholder='password'/>
                        <input type='submit' name='submit'/>
                    </form>
                    '''
        case 'POST':
            password = request.form['password']
            if check_password_hash(current_user.password, password):
                mgr.db.session.delete(current_user)
                mgr.db.session.commit()
                logout_user()
                return redirect('/')

    return '<h1>something went wrong</h1>\n<p>Wrong password?</p>'

