import os
os.environ['DATABASE_URI'] = 'sqlite:///users.db'
os.environ['SECRET_KEY'] = 'obviously_not_secret_key'
os.environ['DEBUG'] = 'True'

from main import app

app.run('0.0.0.0')