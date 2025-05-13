from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app import db # Importe o objeto db
from flask_login import login_user, logout_user, current_user, login_required

bp = Blueprint('auth_bp', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index')) # Se já logado, vai para a página inicial
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone_number=form.phone_number.data # Adicionado
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Parabéns, você foi registrado com sucesso!', 'success')
        # Loga o usuário automaticamente após o registro
        login_user(user)
        return redirect(url_for('main_bp.index')) # Ou para uma página de "bem-vindo"
    return render_template('auth/register.html', title='Cadastro', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email ou senha inválidos.', 'error')
            return redirect(url_for('auth_bp.login'))
        login_user(user, remember=form.remember_me.data)
        flash(f'Login bem-sucedido, bem-vindo de volta, {user.name}!', 'success')
        
        # Redireciona para a próxima página se ela existir, ou para o index
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'): # Segurança: evita redirecionamento aberto
            next_page = url_for('main_bp.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)

@bp.route('/logout')
@login_required # Garante que apenas usuários logados podem deslogar
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('main_bp.index'))