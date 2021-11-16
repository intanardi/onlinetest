from flask import Flask, render_template
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    csrf.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .exam import exam as exam_blueprint
    app.register_blueprint(exam_blueprint, url_prefix='/candidate/exam')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/feniks/v1/administrator')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/administrator/manage/user')

    from .candidate import candidate as candidate_blueprint
    app.register_blueprint(candidate_blueprint, url_prefix='/candidate')

    from .question import question as question_blueprint
    app.register_blueprint(question_blueprint, url_prefix='/administrator/manage/questions')

    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app
