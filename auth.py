from flask_login import UserMixin, LoginManager
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

# class User(UserMixin):
#     def __init__(self, id: str | None = None) -> None:
#         self.id = id or None
#         super().__init__()

class MyLoginManager(LoginManager):
    def __init__(self, app=None, add_context_processor=True):
        self.db = SQLAlchemy(model_class=Base)

        class User(UserMixin, self.db.Model):
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] # Данил Олегов if empty
            password: Mapped[str]
        self.User = User

        #self.con = sqlite3.connect(db)
        #self.cur = self.con.cursor()
        #self.cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, password TEXT NOT NULL)')

        super().__init__(app, add_context_processor)
        self.user_loader(self._user_loader)
        # self.request_loader(self._request_loader)

    def _user_loader(self, id):
        try:
            return self.User.query.get(int(id))
        except:
            return

    # def _request_loader(self, request):
    #     name = request.form.get('id')
    #     if self.cur.execute('SELECT name FROM users WHERE name = ?', name) is not None:
    #         return User(name)

    def init_app(self, app, add_context_processor=True):
        self.db.init_app(app)
        with app.app_context():
            self.db.create_all()
        return super().init_app(app, add_context_processor)