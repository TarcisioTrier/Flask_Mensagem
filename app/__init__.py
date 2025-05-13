from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os # Adicionado para criar a pasta instance
from datetime import datetime
import re
from markupsafe import Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def nl2br(value):
    escaped_value = escape(value)
    result = '\n\n'.join(f'<p>{p}</p>' for p in _paragraph_re.split(escaped_value))
    result = result.replace('\n', Markup('<br>\n'))
    return Markup(result)

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth_bp.login' # Nome do blueprint de autenticação + nome da rota de login
login.login_message = "Por favor, faça login para acessar esta página."
login.login_message_category = "info" # Para estilizar a mensagem flash

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True) # Habilita a pasta 'instance'
    app.config.from_object(config_class)

    # Garante que a pasta 'instance' exista, onde o SQLite será salvo
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # A pasta já existe

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    
    app.jinja_env.filters['nl2br'] = nl2br

    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.utcnow().year}


    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main_routes import bp as main_bp
    app.register_blueprint(main_bp) 

    from app.routes.contact_routes import bp as contact_bp
    app.register_blueprint(contact_bp)
    
    from app.routes.message_routes import bp as message_bp
    app.register_blueprint(message_bp)
    
    from app import models

    return app