from flask import Blueprint, render_template
from flask_login import login_required, current_user # Adicionado current_user

bp = Blueprint('main_bp', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    # Passe o current_user para o template para que base.html possa usá-lo
    return render_template('index.html', title='Página Inicial')

@bp.route('/profile')
@login_required # Protege esta rota
def profile():
    # Simplesmente renderiza uma página de perfil
    return render_template('profile.html', title='Meu Perfil')