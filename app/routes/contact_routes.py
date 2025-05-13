from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Contact, User # Adicionado User para referência se necessário
from app.forms import ContactForm

# Define o Blueprint
# Usaremos url_prefix='/contacts' para que todas as rotas aqui comecem com /contacts
bp = Blueprint('contact_bp', __name__, url_prefix='/contacts')

@bp.route('/')
@login_required
def list_contacts():
    # Busca os contatos do usuário logado, ordenados por nome
    # Usamos .all() para executar a query e obter a lista de contatos
    page = request.args.get('page', 1, type=int) # Para paginação futura
    contacts_pagination = Contact.query.filter_by(user_id=current_user.id).order_by(Contact.name.asc()).paginate(page=page, per_page=10, error_out=False)
    contacts = contacts_pagination.items
    return render_template('contacts/list_contacts.html',
                           title="Meus Contatos",
                           contacts=contacts,
                           pagination=contacts_pagination)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    form = ContactForm()
    if form.validate_on_submit():
        new_contact = Contact(
            name=form.name.data,
            email=form.email.data if form.email.data else None, # Salva None se vazio
            phone_number=form.phone_number.data,
            owner=current_user # Associa o contato ao usuário logado
        )
        db.session.add(new_contact)
        db.session.commit()
        flash(f'Contato "{new_contact.name}" adicionado com sucesso!', 'success')
        return redirect(url_for('contact_bp.list_contacts'))
    return render_template('contacts/contact_form.html', title="Novo Contato", form=form, legend="Novo Contato")

@bp.route('/<int:contact_id>/delete', methods=['POST']) # Aceita apenas POST
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id) # Busca ou retorna 404

    # Verifica se o contato pertence ao usuário logado
    if contact.user_id != current_user.id:
        flash('Você não tem permissão para excluir este contato.', 'error')
        # Ou talvez um abort(403) - Forbidden
        return redirect(url_for('contact_bp.list_contacts'))

    try:
        db.session.delete(contact)
        db.session.commit()
        flash(f'Contato "{contact.name}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback() # Desfaz em caso de erro
        flash(f'Erro ao excluir o contato: {str(e)}', 'error')

    return redirect(url_for('contact_bp.list_contacts'))

@bp.route('/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    # Verifica se o contato pertence ao usuário logado
    if contact.user_id != current_user.id:
        flash('Você não tem permissão para editar este contato.', 'error')
        # Ou abort(403)
        return redirect(url_for('contact_bp.list_contacts'))

    form = ContactForm(obj=contact) # Pré-popula o formulário com dados do objeto 'contact'

    if form.validate_on_submit():
        try:
            # Atualiza os dados do objeto 'contact' com os dados do formulário
            contact.name = form.name.data
            contact.email = form.email.data if form.email.data else None
            contact.phone_number = form.phone_number.data
            # Não precisa adicionar à sessão, pois o objeto já está nela
            db.session.commit()
            flash(f'Contato "{contact.name}" atualizado com sucesso!', 'success')
            return redirect(url_for('contact_bp.list_contacts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o contato: {str(e)}', 'error')
    elif request.method == 'GET':
        # Se for GET, apenas preenche o formulário com os dados existentes
        # (isso já foi feito na inicialização com obj=contact, mas é bom saber)
        pass # form.process(obj=contact) seria outra forma

    # Renderiza o mesmo template do 'add_contact', mas com dados preenchidos
    return render_template('contacts/contact_form.html',
                           title="Editar Contato",
                           form=form,
                           legend=f"Editar Contato: {contact.name}") # Passa uma legenda diferente