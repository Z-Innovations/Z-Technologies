from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

class Base(DeclarativeBase):
    pass

class MyLoginManager(LoginManager):
    def __init__(self, app=None, add_context_processor=True):
        self.db = SQLAlchemy(model_class=Base)

        class User(UserMixin, self.db.Model):
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] # Данил Олегов if empty
            password: Mapped[str]
        self.User = User

        self.bp = Blueprint('auth', __name__, url_prefix='/auth')
        self.bp.route('/register', methods=('GET', 'POST'))(self.register)
        self.bp.route('/unregister', methods=('GET', 'POST'))(self.unregister)
        self.bp.route('/login', methods=('GET', 'POST'))(self.login)
        self.bp.route('/logout')(self.logout)

        super().__init__(app, add_context_processor)
        self.user_loader(self._user_loader)

    def _user_loader(self, id):
        try:
            return self.User.query.get(int(id))
        except: pass

    def init_app(self, app, add_context_processor=True):
        self.db.init_app(app)
        with app.app_context():
            self.db.create_all()
        return super().init_app(app, add_context_processor)

    def register(self):
        match request.method:
            case 'GET':
                return render_template('login_register.html', mode=0)
            case 'POST':
                name, password = request.form['name'], request.form['password']
                user = self.User.query.filter_by(name=name).first()
                if not user and name and password:
                    user = self.User(name=name, password=generate_password_hash(password))
                    self.db.session.add(user)
                    self.db.session.commit()
                    login_user(user)
                    return redirect(url_for('protected'))
        return render_template('info.html', title="something went wrong")

    @login_required
    def unregister(self):
        match request.method:
            case 'GET':
                return render_template('login_register.html', mode=2)
            case 'POST':
                password = request.form['password']
                if check_password_hash(current_user.password, password):
                    self.db.session.delete(current_user)
                    self.db.session.commit()
                    logout_user()
                    return redirect('/')
        return render_template('info.html', title="something went wrong", extra="Wrong password?")

    def login(self):
        if request.method == 'GET':
            return render_template('login_register.html', mode=1)

        name, password = request.form['name'], request.form['password']
        user = self.User.query.filter_by(name=name).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('protected'))

        return render_template('info.html', title="Bad login")

    def logout(self):
        logout_user()
        return render_template('info.html', title="Logged out")