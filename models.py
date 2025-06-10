from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    """Modèle pour les administrateurs"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Formation(db.Model):
    """Modèle pour les formations"""
    __tablename__ = 'formations'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duree = db.Column(db.String(100))
    niveau_requis = db.Column(db.String(200))
    debouches = db.Column(db.Text)
    places_disponibles = db.Column(db.Integer, default=0)
    prix = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    candidatures = db.relationship('Candidature', backref='formation', lazy=True)

class Candidature(db.Model):
    """Modèle pour les candidatures"""
    __tablename__ = 'candidatures'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_dossier = db.Column(db.String(20), unique=True, nullable=False)
    
    # Informations personnelles
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date, nullable=False)
    lieu_naissance = db.Column(db.String(200), nullable=False)
    sexe = db.Column(db.String(10), nullable=False)
    nationalite = db.Column(db.String(100), nullable=False)
    
    # Contact
    telephone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    adresse = db.Column(db.Text, nullable=False)
    
    # Formation
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    niveau_etude = db.Column(db.String(200), nullable=False)
    etablissement_origine = db.Column(db.String(200))
    
    # Documents
    cv_filename = db.Column(db.String(200))
    diplome_filename = db.Column(db.String(200))
    photo_filename = db.Column(db.String(200))
    autres_documents = db.Column(db.Text)  # JSON string for additional documents
    
    # Statut
    statut = db.Column(db.String(50), default='En attente')  # En attente, Accepté, Rejeté
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
    date_traitement = db.Column(db.DateTime)
    commentaires_admin = db.Column(db.Text)
    
    # Session de concours
    session_concours = db.Column(db.String(100))

class Actualite(db.Model):
    """Modèle pour les actualités"""
    __tablename__ = 'actualites'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    resume = db.Column(db.Text)
    image_filename = db.Column(db.String(200))
    is_published = db.Column(db.Boolean, default=True)
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Auteur
    auteur_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    auteur = db.relationship('Admin', backref='actualites')

class MembreEquipe(db.Model):
    """Modèle pour les membres de l'équipe"""
    __tablename__ = 'membres_equipe'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    poste = db.Column(db.String(200), nullable=False)
    departement = db.Column(db.String(200))
    specialites = db.Column(db.Text)
    formation_academique = db.Column(db.Text)
    experience = db.Column(db.Text)
    email = db.Column(db.String(120))
    telephone = db.Column(db.String(20))
    photo_filename = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    ordre_affichage = db.Column(db.Integer, default=0)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class Configuration(db.Model):
    """Modèle pour la configuration du site"""
    __tablename__ = 'configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    nom_institut = db.Column(db.String(200), default="Institut National de Formation Agricole de Tové")
    adresse = db.Column(db.Text)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    site_web = db.Column(db.String(200))
    
    # Réseaux sociaux
    facebook = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    
    # Textes personnalisables
    mission = db.Column(db.Text)
    vision = db.Column(db.Text)
    historique = db.Column(db.Text)
    
    # Paramètres de candidature
    session_concours_actuelle = db.Column(db.String(100))
    candidatures_ouvertes = db.Column(db.Boolean, default=True)
    date_limite_candidature = db.Column(db.Date)
    
    # Messages
    message_accueil = db.Column(db.Text)
    message_candidature = db.Column(db.Text)
    
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contact(db.Model):
    """Modèle pour les messages de contact"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    sujet = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    reponse = db.Column(db.Text)
    date_reponse = db.Column(db.DateTime)
