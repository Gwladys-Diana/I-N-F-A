from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from app import app, db, allowed_file
from models import Formation, Candidature, Actualite, MembreEquipe, Configuration, Contact
from forms import CandidatureForm, ContactForm
import os
import uuid
from datetime import datetime
import json

@app.route('/')
def index():
    """Page d'accueil"""
    # Récupérer les dernières actualités
    actualites = Actualite.query.filter_by(is_published=True).order_by(Actualite.date_publication.desc()).limit(3).all()
    
    # Récupérer les formations principales
    formations = Formation.query.filter_by(is_active=True).limit(4).all()
    
    # Configuration du site
    config = Configuration.query.first()
    if not config:
        config = Configuration()
        db.session.add(config)
        db.session.commit()
    
    return render_template('index.html', 
                         actualites=actualites, 
                         formations=formations,
                         config=config)

@app.route('/formations')
def formations():
    """Page des formations"""
    formations = Formation.query.filter_by(is_active=True).all()
    return render_template('formations.html', formations=formations)

@app.route('/formation/<int:formation_id>')
def formation_detail(formation_id):
    """Détail d'une formation"""
    formation = Formation.query.get_or_404(formation_id)
    return render_template('formation_detail.html', formation=formation)

@app.route('/candidature', methods=['GET', 'POST'])
def candidature():
    """Page de candidature"""
    config = Configuration.query.first()
    
    # Vérifier si les candidatures sont ouvertes
    if config and not config.candidatures_ouvertes:
        flash('Les candidatures sont actuellement fermées.', 'warning')
        return redirect(url_for('index'))
    
    # Vérifier la date limite
    if config and config.date_limite_candidature and config.date_limite_candidature < datetime.now().date():
        flash('La date limite de candidature est dépassée.', 'warning')
        return redirect(url_for('index'))
    
    form = CandidatureForm()
    form.formation_id.choices = [(f.id, f.nom) for f in Formation.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        try:
            # Générer un numéro de dossier unique
            numero_dossier = f"INFA{datetime.now().year}{str(uuid.uuid4())[:8].upper()}"
            
            # Créer la candidature
            candidature = Candidature(
                numero_dossier=numero_dossier,
                nom=form.nom.data,
                prenom=form.prenom.data,
                date_naissance=form.date_naissance.data,
                lieu_naissance=form.lieu_naissance.data,
                sexe=form.sexe.data,
                nationalite=form.nationalite.data,
                telephone=form.telephone.data,
                email=form.email.data,
                adresse=form.adresse.data,
                formation_id=form.formation_id.data,
                niveau_etude=form.niveau_etude.data,
                etablissement_origine=form.etablissement_origine.data,
                session_concours=config.session_concours_actuelle if config else "2024"
            )
            
            # Traitement des fichiers uploadés
            upload_folder = current_app.config['UPLOAD_FOLDER']
            
            if form.cv.data and allowed_file(form.cv.data.filename):
                cv_filename = f"{numero_dossier}_cv_{form.cv.data.filename}"
                form.cv.data.save(os.path.join(upload_folder, cv_filename))
                candidature.cv_filename = cv_filename
            
            if form.diplome.data and allowed_file(form.diplome.data.filename):
                diplome_filename = f"{numero_dossier}_diplome_{form.diplome.data.filename}"
                form.diplome.data.save(os.path.join(upload_folder, diplome_filename))
                candidature.diplome_filename = diplome_filename
            
            if form.photo.data and allowed_file(form.photo.data.filename):
                photo_filename = f"{numero_dossier}_photo_{form.photo.data.filename}"
                form.photo.data.save(os.path.join(upload_folder, photo_filename))
                candidature.photo_filename = photo_filename
            
            db.session.add(candidature)
            db.session.commit()
            
            flash(f'Votre candidature a été soumise avec succès. Numéro de dossier: {numero_dossier}', 'success')
            return redirect(url_for('candidature_success', numero=numero_dossier))
            
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la soumission de votre candidature.', 'error')
            current_app.logger.error(f"Erreur candidature: {e}")
    
    formations = Formation.query.filter_by(is_active=True).all()
    return render_template('candidature.html', form=form, formations=formations, config=config)

@app.route('/candidature/success/<numero>')
def candidature_success(numero):
    """Page de confirmation de candidature"""
    candidature = Candidature.query.filter_by(numero_dossier=numero).first_or_404()
    return render_template('candidature_success.html', candidature=candidature)

@app.route('/resultats')
def resultats():
    """Page des résultats"""
    config = Configuration.query.first()
    session_actuelle = config.session_concours_actuelle if config else "2024"
    
    # Récupérer les candidats acceptés pour la session actuelle
    candidats_acceptes = Candidature.query.filter_by(
        statut='Accepté',
        session_concours=session_actuelle
    ).join(Formation).order_by(Formation.nom, Candidature.nom).all()
    
    return render_template('resultats.html', 
                         candidats=candidats_acceptes,
                         session=session_actuelle)

@app.route('/resultats/recherche')
def resultats_recherche():
    """Recherche de résultats par nom ou numéro"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('resultats'))
    
    # Rechercher par nom ou numéro de dossier
    candidats = Candidature.query.filter(
        db.or_(
            Candidature.nom.ilike(f'%{query}%'),
            Candidature.prenom.ilike(f'%{query}%'),
            Candidature.numero_dossier.ilike(f'%{query}%')
        ),
        Candidature.statut == 'Accepté'
    ).join(Formation).all()
    
    return render_template('resultats_recherche.html', 
                         candidats=candidats,
                         query=query)

@app.route('/actualites')
def actualites():
    """Page des actualités"""
    page = request.args.get('page', 1, type=int)
    actualites = Actualite.query.filter_by(is_published=True)\
        .order_by(Actualite.date_publication.desc())\
        .paginate(page=page, per_page=6, error_out=False)
    
    return render_template('actualites.html', actualites=actualites)

@app.route('/actualite/<int:actualite_id>')
def actualite_detail(actualite_id):
    """Détail d'une actualité"""
    actualite = Actualite.query.get_or_404(actualite_id)
    
    # Actualités similaires
    actualites_similaires = Actualite.query.filter(
        Actualite.id != actualite_id,
        Actualite.is_published == True
    ).order_by(Actualite.date_publication.desc()).limit(3).all()
    
    return render_template('actualite_detail.html', 
                         actualite=actualite,
                         actualites_similaires=actualites_similaires)

@app.route('/equipe')
def equipe():
    """Page de l'équipe"""
    membres = MembreEquipe.query.filter_by(is_active=True)\
        .order_by(MembreEquipe.ordre_affichage, MembreEquipe.nom).all()
    
    return render_template('equipe.html', membres=membres)

@app.route('/infrastructures')
def infrastructures():
    """Page des infrastructures"""
    return render_template('infrastructures.html')

@app.route('/historique')
def historique():
    """Page de l'historique"""
    config = Configuration.query.first()
    return render_template('historique.html', config=config)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Page de contact"""
    form = ContactForm()
    
    if form.validate_on_submit():
        try:
            contact_msg = Contact(
                nom=form.nom.data,
                email=form.email.data,
                sujet=form.sujet.data,
                message=form.message.data
            )
            
            db.session.add(contact_msg)
            db.session.commit()
            
            flash('Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de l\'envoi de votre message.', 'error')
            current_app.logger.error(f"Erreur contact: {e}")
    
    config = Configuration.query.first()
    return render_template('contact.html', form=form, config=config)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Contexte global pour les templates
@app.context_processor
def inject_config():
    config = Configuration.query.first()
    if not config:
        config = Configuration()
    return dict(site_config=config)
