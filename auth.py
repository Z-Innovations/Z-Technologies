from flask_login import UserMixin, LoginManager, current_user, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate

ONLY_DISCRIMINATOR = False

class Base(DeclarativeBase):
    pass

class MyLoginManager(LoginManager):
    def __init__(self, app=None, add_context_processor=True):
        self.db = SQLAlchemy(model_class=Base)
        self.migrate = Migrate(db=self.db)

        class User(UserMixin, self.db.Model):
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None] = mapped_column(unique=True) # Олег Данилов if empty
            password: Mapped[str]
            discriminator: Mapped[int | None] = mapped_column(unique=True)
            creditcard_number: Mapped[int | None]
            creditcard_valid_till: Mapped[str | None]
            creditcard_3_digits: Mapped[int | None]
        self.User = User

        self.bp = Blueprint('auth', __name__, url_prefix='/auth')
        for f in 'register unregister login edit_password credit_card switch_to_discriminator'.split():
            self.register_page(getattr(self, f))
        self.register_page(self.logout, False)

        super().__init__(app, add_context_processor)
        self.user_loader(self._user_loader)

    def register_page(self, func, allow_post=True):
        kw = {'methods': ('GET', 'POST')} if allow_post else {}
        self.bp.route(f'/{func.__name__}', **kw)(func)

    def _user_loader(self, id):
        try:
            return self.User.query.get(int(id))
        except: pass

    def init_app(self, app, add_context_processor=True):
        self.db.init_app(app)
        with app.app_context():
            self.db.create_all()
        self.migrate.init_app(app)
        return super().init_app(app, add_context_processor)
    
    @property
    def next_discriminator(self):
        return (self.User.query.with_entities(func.max(self.User.discriminator)).scalar() or 0)+1

    def register(self):
        match request.method:
            case 'GET':
                return render_template('auth/login_register.html', mode=0)
            case 'POST':
                password = request.form.get('password', None)
                if not password:
                    return render_template('info.html', title="password is empty or not given")
                discriminator_mode = request.form.get('mode', 'custom' if request.form.get('name', None) else 'oleg') == 'oleg'
                if ONLY_DISCRIMINATOR and not discriminator_mode:
                    return render_template('info.html', title="only discriminator (OLEG) mode is allowed in this enivonment")
                if not discriminator_mode:
                    name = request.form.get('name', None)
                    if not name:
                        return render_template('info.html', title="name empty or not given")
                    if self.User.query.filter_by(name=name).first():
                        return render_template('info.html', title="user with this name already exists")
                    user = self.User(name=name, password=generate_password_hash(password))
                else:
                    user = self.User(discriminator=self.next_discriminator, password=generate_password_hash(password))
                self.db.session.add(user)
                self.db.session.commit()
                login_user(user)
                return redirect(url_for('protected'))
        return render_template('info.html', title="something went wrong")

    @login_required
    def unregister(self):
        match request.method:
            case 'GET':
                return render_template('auth/login_register.html', mode=2)
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
            return render_template('auth/login_register.html', mode=1)

        password = request.form.get('password', None)
        if not password:
            return render_template('info.html', title="No password provided")
        if not 'name' in request.form and not 'discriminator' in request.form:
            return render_template('info.html', title="No name or discriminator provided")
        key = 'name' if request.form.get('name', None) else 'discriminator'
        user = self.User.query.filter_by(**{key: request.form[key]}).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('protected'))

        return render_template('info.html', title="Bad login")

    def logout(self):
        logout_user()
        return render_template('info.html', title="Logged out")

    def edit_field(self, **kwargs):
        for name, value in kwargs.items():
            setattr(current_user, name, value)
        self.db.session.commit()

    @login_required
    def edit_password(self):
        match request.method:
            case 'GET':
                return render_template('auth/edit_password.html')
            case 'POST':
                old = request.form['old']
                password = request.form['password']
                if check_password_hash(current_user.password, old):
                    self.edit_field(password=generate_password_hash(password))
                    return render_template('info.html', title="Password changed")
        return render_template('info.html', title="something went wrong", extra="Wrong password?")
    
    @login_required
    def credit_card(self):
        match request.method:
            case 'GET':
                return render_template('auth/credit_card.html', number=current_user.creditcard_number, validtill=current_user.creditcard_valid_till or '', three=current_user.creditcard_3_digits)
            case 'POST':
                number = request.form['number']
                validtill = request.form['validtill']
                three = request.form['three']
                self.edit_field(creditcard_number=number, creditcard_valid_till=validtill, creditcard_3_digits=three)
                return render_template('info.html', title="всё")
        return render_template('info.html', title="something went wrong", extra="Wrong password?")
    
    @login_required
    def switch_to_discriminator(self):
        match request.method:
            case 'GET':
                return render_template('auth/edit_password.html', switch_to_discriminator=True)
            case 'POST':
                password = request.form['password']
                if check_password_hash(current_user.password, password):
                    self.edit_field(name=None, discriminator=self.next_discriminator)
                    return render_template('info.html', title="Success")
        return render_template('info.html', title="something went wrong", extra="Wrong password?")