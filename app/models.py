from app import db, login # Importa o 'login' de app/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone # Importe timezone

# Flask-Login precisa desta função para carregar um usuário pelo ID
@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id)) # Use db.session.get para SQLAlchemy 2.0+

class User(UserMixin, db.Model):
    __tablename__ = 'user' # Define o nome da tabela explicitamente

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True) # Adiciona index=True
    phone_number = db.Column(db.String(20), nullable=True) # Celular do usuário
    password_hash = db.Column(db.String(256)) # Aumentado para hashes mais longos

    # Relacionamentos
    contacts = db.relationship('Contact', back_populates='owner', lazy='dynamic', cascade="all, delete-orphan")
    sent_messages = db.relationship('Message', foreign_keys='Message.user_id', back_populates='sender', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name} ({self.email})>'

class Contact(db.Model):
    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True) # Contatos podem não ter email
    phone_number = db.Column(db.String(20), nullable=False) # Celular do contato é obrigatório

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Chave estrangeira para User

    # Relacionamentos
    owner = db.relationship('User', back_populates='contacts')
    messages_to_contact = db.relationship('Message', back_populates='recipient', lazy='dynamic', cascade="all, delete-orphan") # Mensagens onde este contato é o destinatário

    def __repr__(self):
        return f'<Contact {self.name} for User ID {self.user_id}>'

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc)) # Data de envio

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Quem enviou a mensagem
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False) # Para quem a mensagem foi enviada

    # Relacionamentos
    sender = db.relationship('User', back_populates='sent_messages', foreign_keys=[user_id])
    recipient = db.relationship('Contact', back_populates='messages_to_contact')

    def __repr__(self):
        return f'<Message "{self.title}" from User ID {self.user_id} to Contact ID {self.contact_id}>'