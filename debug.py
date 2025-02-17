# docker run  -p 5432:5432 -e POSTGRES_PASSWORD=postgres_password -e POSTGRES_USER=postgres_user -e POSTGRES_DB=postgres postgres:latest

import os
# os.environ['DATABASE_URI'] = 'sqlite:///users.db'
os.environ['DATABASE_URI'] = 'postgresql://postgres_user:postgres_password@localhost/postgres'
os.environ['SECRET_KEY'] = 'obviously_not_secret_key'
os.environ['DEBUG'] = 'True'

from main import app

app.run('0.0.0.0')