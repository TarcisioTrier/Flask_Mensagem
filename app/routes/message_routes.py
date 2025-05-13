from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Message, Contact, User # Adicionado User para referência se necessário
from app.forms import MessageForm

# Define o Blueprint
# Todas as rotas aqui começarão com /messages
bp = Blueprint('message_bp', __name__, url_prefix='/messages')

# Rota para listar mensagens de um contato específico e enviar nova mensagem
@bp.route('/contact/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def list_messages_for_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    # Segurança: Verifique se o contato pertence ao usuário logado
    if contact.user_id != current_user.id:
        flash('Você não tem permissão para ver ou enviar mensagens para este contato.', 'error')
        return redirect(url_for('contact_bp.list_contacts'))

    form = MessageForm() # Formulário para enviar nova mensagem

    if form.validate_on_submit():
        # Processar o envio da nova mensagem
        new_message = Message(
            title=form.title.data,
            body=form.body.data,
            sender=current_user, # O usuário logado é o remetente
            recipient=contact     # O contato selecionado é o destinatário
        )
        db.session.add(new_message)
        db.session.commit()
        flash('Mensagem enviada com sucesso!', 'success')
        # Redireciona para a mesma página para ver a mensagem enviada e limpar o formulário
        return redirect(url_for('message_bp.list_messages_for_contact', contact_id=contact.id))

    # Listar mensagens existentes entre o usuário e este contato
    # Ordenar da mais recente para a mais antiga
    messages = Message.query.filter_by(user_id=current_user.id, contact_id=contact.id)\
                            .order_by(Message.timestamp.desc()).all()

    return render_template('messages/message_list_and_form.html',
                           title=f"Mensagens com {contact.name}",
                           contact=contact,
                           form=form,
                           messages=messages)