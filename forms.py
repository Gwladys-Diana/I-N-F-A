from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, FloatField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from wtforms.widgets import TextArea

class CandidatureForm(FlaskForm):
    """Formulaire de candidature"""
    # Informations personnelles
    nom = StringField('Nom', validators=[DataRequired(), Length(min=2, max=100)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=100)])
    date_naissance = DateField('Date de naissance', validators=[DataRequired()])
    lieu_naissance = StringField('Lieu de naissance', validators=[DataRequired(), Length(max=200)])
    sexe = SelectField('Sexe', choices=[('M', 'Masculin'), ('F', 'Féminin')], validators=[DataRequired()])
    nationalite = StringField('Nationalité', validators=[DataRequired(), Length(max=100)])
    
    # Contact
    telephone = StringField('Téléphone', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    adresse = TextAreaField('Adresse complète', validators=[DataRequired()])
    
    # Formation
    formation_id = SelectField('Formation souhaitée', coerce=int, validators=[DataRequired()])
    niveau_etude = StringField('Niveau d\'études', validators=[DataRequired(), Length(max=200)])
    etablissement_origine = StringField('Établissement d\'origine', validators=[Optional(), Length(max=200)])
    
    # Documents
    cv = FileField('CV (PDF)', validators=[
        FileAllowed(['pdf'], 'Seuls les fichiers PDF sont autorisés!')
    ])
    diplome = FileField('Diplôme (PDF)', validators=[
        FileAllowed(['pdf'], 'Seuls les fichiers PDF sont autorisés!')
    ])
    photo = FileField('Photo d\'identité', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Seules les images JPG et PNG sont autorisées!')
    ])
    
    submit = SubmitField('Soumettre ma candidature')

class ContactForm(FlaskForm):
    """Formulaire de contact"""
    nom = StringField('Nom complet', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    sujet = StringField('Sujet', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Envoyer le message')

class AdminLoginForm(FlaskForm):
    """Formulaire de connexion admin"""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class FormationForm(FlaskForm):
    """Formulaire de formation"""
    nom = StringField('Nom de la formation', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    duree = StringField('Durée', validators=[Optional(), Length(max=100)])
    niveau_requis = StringField('Niveau requis', validators=[Optional(), Length(max=200)])
    debouches = TextAreaField('Débouchés')
    places_disponibles = IntegerField('Places disponibles', validators=[Optional(), NumberRange(min=0)])
    prix = FloatField('Prix (FCFA)', validators=[Optional(), NumberRange(min=0)])
    is_active = BooleanField('Formation active')
    submit = SubmitField('Enregistrer')

class ActualiteForm(FlaskForm):
    """Formulaire d'actualité"""
    titre = StringField('Titre', validators=[DataRequired(), Length(max=200)])
    resume = TextAreaField('Résumé', validators=[Optional(), Length(max=500)])
    contenu = TextAreaField('Contenu', validators=[DataRequired()], widget=TextArea())
    image = FileField('Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Seules les images JPG et PNG sont autorisées!')
    ])
    is_published = BooleanField('Publier immédiatement')
    submit = SubmitField('Enregistrer')

class MembreEquipeForm(FlaskForm):
    """Formulaire de membre d'équipe"""
    nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(max=100)])
    poste = StringField('Poste', validators=[DataRequired(), Length(max=200)])
    departement = StringField('Département', validators=[Optional(), Length(max=200)])
    specialites = TextAreaField('Spécialités')
    formation_academique = TextAreaField('Formation académique')
    experience = TextAreaField('Expérience professionnelle')
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    photo = FileField('Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Seules les images JPG et PNG sont autorisées!')
    ])
    is_active = BooleanField('Membre actif', default=True)
    ordre_affichage = IntegerField('Ordre d\'affichage', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Enregistrer')

class ConfigurationForm(FlaskForm):
    """Formulaire de configuration"""
    nom_institut = StringField('Nom de l\'institut', validators=[DataRequired(), Length(max=200)])
    adresse = TextAreaField('Adresse')
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    site_web = StringField('Site web', validators=[Optional(), Length(max=200)])
    
    # Réseaux sociaux
    facebook = StringField('Facebook', validators=[Optional(), Length(max=200)])
    twitter = StringField('Twitter', validators=[Optional(), Length(max=200)])
    linkedin = StringField('LinkedIn', validators=[Optional(), Length(max=200)])
    
    # Textes
    mission = TextAreaField('Mission')
    vision = TextAreaField('Vision')
    historique = TextAreaField('Historique')
    
    # Candidatures
    session_concours_actuelle = StringField('Session de concours actuelle', validators=[Optional(), Length(max=100)])
    candidatures_ouvertes = BooleanField('Candidatures ouvertes')
    date_limite_candidature = DateField('Date limite de candidature', validators=[Optional()])
    
    # Messages
    message_accueil = TextAreaField('Message d\'accueil')
    message_candidature = TextAreaField('Message de candidature')
    
    submit = SubmitField('Enregistrer')
