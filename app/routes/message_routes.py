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
    
@bp.route('/<int:message_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_message(message_id):
    message = Message.query.get_or_404(message_id)

    # Segurança: Verifique se o usuário logado é o remetente da mensagem
    if message.user_id != current_user.id:
        flash('Você não tem permissão para editar esta mensagem.', 'danger')
        # Tenta redirecionar de volta para a conversa original, se possível
        if message.recipient: # Se a mensagem tem um destinatário (contato)
             return redirect(url_for('message_bp.list_messages_for_contact', contact_id=message.contact_id))
        return redirect(url_for('main_bp.index')) # Fallback

    form = MessageForm(obj=message) # Pré-popula o formulário com dados da mensagem

    if form.validate_on_submit():
        try:
            message.title = form.title.data
            message.body = form.body.data
            # message.timestamp = datetime.utcnow() # Opcional: atualizar o timestamp na edição?
            # Decidimos não atualizar o timestamp para manter o original do envio.
            db.session.commit()
            flash('Mensagem atualizada com sucesso!', 'success')
            return redirect(url_for('message_bp.list_messages_for_contact', contact_id=message.contact_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar a mensagem: {str(e)}', 'danger')

    return render_template('messages/edit_message.html',
                           title="Editar Mensagem",
                           form=form,
                           message_id=message.id, # Para o action do formulário no template
                           contact_id=message.contact_id) # Para o botão Cancelar

# Rota para EXCLUIR uma mensagem
@bp.route('/<int:message_id>/delete', methods=['POST']) # Apenas POST
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    contact_id_redirect = message.contact_id # Salva para redirecionamento

    # Segurança: Verifique se o usuário logado é o remetente da mensagem
    if message.user_id != current_user.id:
        flash('Você não tem permissão para excluir esta mensagem.', 'danger')
        if contact_id_redirect:
            return redirect(url_for('message_bp.list_messages_for_contact', contact_id=contact_id_redirect))
        return redirect(url_for('main_bp.index'))

    try:
        db.session.delete(message)
        db.session.commit()
        flash('Mensagem excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir a mensagem: {str(e)}', 'danger')

    # Redireciona para a lista de mensagens do contato original
    if contact_id_redirect:
        return redirect(url_for('message_bp.list_messages_for_contact', contact_id=contact_id_redirect))
    return redirect(url_for('main_bp.index')) # Fallback se não houver contact_id (improvável neste fluxo)