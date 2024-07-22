from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
DB_NAME = "database.db"
mail=Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAIL_SERVER']='smtp-relay.brevo.com'
    app.config['MAIL_PORT']=587
    app.config['MAIL_USE_TLS']=True
    app.config['MAIL_USERNAME']='78f0b3001@smtp-brevo.com'
    app.config['MAIL_PASSWORD']='2TO9K6V5GSZAIJvF'
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'darkkamal78@gamil.com'
    db.init_app(app)

    mail.init_app(app)

    from .views import views
    from .auth import auth
    from .auth import auth_v2 as auth_blueprint
    
    app.register_blueprint(auth_blueprint,url_prefix="/")
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Post, Comment, Like

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Created database!")