from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_required, current_user

app = Flask(__name__)
db = SQLAlchemy()

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models import User


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


# blueprint for auth routes in our app
from auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


if __name__ == '__main__':
    app.run(ssl_context="adhoc")
