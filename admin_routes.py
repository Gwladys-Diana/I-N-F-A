from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import Admin, Formation, Candidature, Actualite, MembreEquipe, Configuration, Contact
from forms import AdminLoginForm, FormationForm, ActualiteForm, MembreEquipeForm, ConfigurationForm
from werkzeug.security import generate_password_hash
import os
from datetime import datetime, timedelta
from sqlalchemy import func, extract

# Créer le blueprint admin
admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion admin"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin_user = Admin.query.filter_by(username=form.username.data).first()
        
        if admin_user and admin_user.check_password(form.password.data) and admin_user.is_active:
            login_user(admin_user, remember=form.remember_me.data)
            
            # Mettre à jour la dernière connexion
            admin_user.derniere_connexion = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/admin'):
                next_page = url_for('admin.dashboard')
            
            flash('Connexion réussie!', 'success')
            return redirect(next_page)
        else:
            flash('Nom d\'utilisateur ou mot de passe invalide.', 'error')
    
    return render_template('admin/login.html', form=form)

@admin.route('/logout')
@login_required
def logout():
    """Déconnexion admin"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('admin.login'))

@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord administrateur"""
    # Statistiques générales
    total_candidatures = Candidature.query.count()
    candidatures_en_attente = Candidature.query.filter_by(statut='En attente').count()
    candidatures_acceptees = Candidature.query.filter_by(statut='Accepté').count()
    candidatures_rejetees = Candidature.query.filter_by(statut='Rejeté').count()
    
    # Statistiques par formation
    stats_formations = db.session.query(
        Formation.nom,
        func.count(Candidature.id).label('nb_candidatures')
    ).join(Candidature).group_by(Formation.id, Formation.nom).all()
    
    # Candidatures récentes
    candidatures_recentes = Candidature.query.order_by(
        Candidature.date_soumission.desc()
    ).limit(5).all()
    
    # Statistiques par mois (derniers 6 mois)
    six_mois_ago = datetime.now() - timedelta(days=180)
    stats_mensuelles = db.session.query(
        extract('month', Candidature.date_soumission).label('mois'),
        extract('year', Candidature.date_soumission).label('annee'),
        func.count(Candidature.id).label('nb_candidatures')
    ).filter(
        Candidature.date_soumission >= six_mois_ago
    ).group_by(
        extract('year', Candidature.date_soumission),
        extract('month', Candidature.date_soumission)
    ).order_by('annee', 'mois').all()
    
    # Messages de contact non lus
    messages_non_lus = Contact.query.filter_by(is_read=False).count()
    
    return render_template('admin/dashboard.html',
                         total_candidatures=total_candidatures,
                         candidatures_en_attente=candidatures_en_attente,
                         candidatures_acceptees=candidatures_acceptees,
                         candidatures_rejetees=candidatures_rejetees,
                         stats_formations=stats_formations,
                         candidatures_recentes=candidatures_recentes,
                         stats_mensuelles=stats_mensuelles,
                         messages_non_lus=messages_non_lus)

@admin.route('/candidatures')
@login_required
def candidatures():
    """Liste des candidatures"""
    page = request.args.get('page', 1, type=int)
    statut = request.args.get('statut', '')
    formation_id = request.args.get('formation', '', type=int)
    search = request.args.get('search', '')
    
    query = Candidature.query
    
    # Filtres
    if statut:
        query = query.filter_by(statut=statut)
    
    if formation_id:
        query = query.filter_by(formation_id=formation_id)
    
    if search:
        query = query.filter(
            db.or_(
                Candidature.nom.ilike(f'%{search}%'),
                Candidature.prenom.ilike(f'%{search}%'),
                Candidature.numero_dossier.ilike(f'%{search}%'),
                Candidature.email.ilike(f'%{search}%')
            )
        )
    
    candidatures = query.order_by(Candidature.date_soumission.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    formations = Formation.query.filter_by(is_active=True).all()
    
    return render_template('admin/candidatures.html',
                         candidatures=candidatures,
                         formations=formations,
                         current_statut=statut,
                         current_formation=formation_id,
                         current_search=search)

@admin.route('/candidature/<int:candidature_id>')
@login_required
def candidature_detail(candidature_id):
    """Détail d'une candidature"""
    candidature = Candidature.query.get_or_404(candidature_id)
    return render_template('admin/candidature_detail.html', candidature=candidature)

@admin.route('/candidature/<int:candidature_id>/traiter', methods=['POST'])
@login_required
def traiter_candidature(candidature_id):
    """Traiter une candidature (accepter/rejeter)"""
    candidature = Candidature.query.get_or_404(candidature_id)
    
    action = request.form.get('action')
    commentaires = request.form.get('commentaires', '')
    
    if action == 'accepter':
        candidature.statut = 'Accepté'
        flash(f'Candidature de {candidature.nom} {candidature.prenom} acceptée.', 'success')
    elif action == 'rejeter':
        candidature.statut = 'Rejeté'
        flash(f'Candidature de {candidature.nom} {candidature.prenom} rejetée.', 'warning')
    
    candidature.date_traitement = datetime.utcnow()
    candidature.commentaires_admin = commentaires
    
    db.session.commit()
    
    return redirect(url_for('admin.candidature_detail', candidature_id=candidature_id))

@admin.route('/formations')
@login_required
def formations():
    """Liste des formations"""
    formations = Formation.query.order_by(Formation.nom).all()
    return render_template('admin/formations.html', formations=formations)

@admin.route('/formation/nouvelle', methods=['GET', 'POST'])
@login_required
def nouvelle_formation():
    """Créer une nouvelle formation"""
    form = FormationForm()
    
    if form.validate_on_submit():
        formation = Formation(
            nom=form.nom.data,
            description=form.description.data,
            duree=form.duree.data,
            niveau_requis=form.niveau_requis.data,
            debouches=form.debouches.data,
            places_disponibles=form.places_disponibles.data,
            prix=form.prix.data,
            is_active=form.is_active.data
        )
        
        db.session.add(formation)
        db.session.commit()
        
        flash('Formation créée avec succès!', 'success')
        return redirect(url_for('admin.formations'))
    
    return render_template('admin/formation_form.html', form=form, title="Nouvelle formation")

@admin.route('/formation/<int:formation_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_formation(formation_id):
    """Modifier une formation"""
    formation = Formation.query.get_or_404(formation_id)
    form = FormationForm(obj=formation)
    
    if form.validate_on_submit():
        form.populate_obj(formation)
        formation.date_modification = datetime.utcnow()
        
        db.session.commit()
        
        flash('Formation modifiée avec succès!', 'success')
        return redirect(url_for('admin.formations'))
    
    return render_template('admin/formation_form.html', 
                         form=form, 
                         formation=formation,
                         title="Modifier formation")

@admin.route('/formation/<int:formation_id>/supprimer', methods=['POST'])
@login_required
def supprimer_formation(formation_id):
    """Supprimer une formation"""
    formation = Formation.query.get_or_404(formation_id)
    
    # Vérifier s'il y a des candidatures associées
    if formation.candidatures:
        flash('Impossible de supprimer cette formation car elle a des candidatures associées.', 'error')
    else:
        db.session.delete(formation)
        db.session.commit()
        flash('Formation supprimée avec succès!', 'success')
    
    return redirect(url_for('admin.formations'))

@admin.route('/actualites')
@login_required
def actualites():
    """Liste des actualités"""
    actualites = Actualite.query.order_by(Actualite.date_creation.desc()).all()
    return render_template('admin/actualites.html', actualites=actualites)

@admin.route('/actualite/nouvelle', methods=['GET', 'POST'])
@login_required
def nouvelle_actualite():
    """Créer une nouvelle actualité"""
    form = ActualiteForm()
    
    if form.validate_on_submit():
        actualite = Actualite(
            titre=form.titre.data,
            contenu=form.contenu.data,
            resume=form.resume.data,
            is_published=form.is_published.data,
            auteur_id=current_user.id
        )
        
        # Traitement de l'image si présente
        if form.image.data:
            # Ici vous pourriez ajouter la logique de traitement d'image
            pass
        
        db.session.add(actualite)
        db.session.commit()
        
        flash('Actualité créée avec succès!', 'success')
        return redirect(url_for('admin.actualites'))
    
    return render_template('admin/actualite_form.html', form=form, title="Nouvelle actualité")

@admin.route('/actualite/<int:actualite_id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_actualite(actualite_id):
    """Modifier une actualité"""
    actualite = Actualite.query.get_or_404(actualite_id)
    form = ActualiteForm(obj=actualite)
    
    if form.validate_on_submit():
        form.populate_obj(actualite)
        actualite.date_modification = datetime.utcnow()
        
        db.session.commit()
        
        flash('Actualité modifiée avec succès!', 'success')
        return redirect(url_for('admin.actualites'))
    
    return render_template('admin/actualite_form.html', 
                         form=form,
                         actualite=actualite,
                         title="Modifier actualité")

@admin.route('/equipe')
@login_required
def equipe():
    """Liste des membres de l'équipe"""
    membres = MembreEquipe.query.order_by(MembreEquipe.ordre_affichage, MembreEquipe.nom).all()
    return render_template('admin/equipe.html', membres=membres)

@admin.route('/membre/nouveau', methods=['GET', 'POST'])
@login_required
def nouveau_membre():
    """Ajouter un nouveau membre à l'équipe"""
    form = MembreEquipeForm()
    
    if form.validate_on_submit():
        membre = MembreEquipe(
            nom=form.nom.data,
            prenom=form.prenom.data,
            poste=form.poste.data,
            departement=form.departement.data,
            specialites=form.specialites.data,
            formation_academique=form.formation_academique.data,
            experience=form.experience.data,
            email=form.email.data,
            telephone=form.telephone.data,
            is_active=form.is_active.data,
            ordre_affichage=form.ordre_affichage.data
        )
        
        db.session.add(membre)
        db.session.commit()
        
        flash('Membre ajouté avec succès!', 'success')
        return redirect(url_for('admin.equipe'))
    
    return render_template('admin/membre_form.html', form=form, title="Nouveau membre")

@admin.route('/resultats')
@login_required
def resultats():
    """Gestion des résultats"""
    config = Configuration.query.first()
    session_actuelle = config.session_concours_actuelle if config else "2024"
    
    # Candidatures par session
    candidatures_session = Candidature.query.filter_by(
        session_concours=session_actuelle
    ).order_by(Candidature.nom).all()
    
    # Statistiques
    stats = {
        'total': len(candidatures_session),
        'acceptes': len([c for c in candidatures_session if c.statut == 'Accepté']),
        'rejetes': len([c for c in candidatures_session if c.statut == 'Rejeté']),
        'en_attente': len([c for c in candidatures_session if c.statut == 'En attente'])
    }
    
    return render_template('admin/resultats.html',
                         candidatures=candidatures_session,
                         session=session_actuelle,
                         stats=stats)

@admin.route('/publier-resultats', methods=['POST'])
@login_required
def publier_resultats():
    """Publier les résultats d'une session"""
    session_concours = request.form.get('session')
    
    # Ici vous pourriez ajouter une logique de publication
    # Par exemple, envoyer des notifications, générer des PDFs, etc.
    
    flash(f'Résultats de la session {session_concours} publiés avec succès!', 'success')
    return redirect(url_for('admin.resultats'))

@admin.route('/configuration', methods=['GET', 'POST'])
@login_required
def configuration():
    """Configuration du site"""
    config = Configuration.query.first()
    if not config:
        config = Configuration()
        db.session.add(config)
        db.session.commit()
    
    form = ConfigurationForm(obj=config)
    
    if form.validate_on_submit():
        form.populate_obj(config)
        config.date_modification = datetime.utcnow()
        
        db.session.commit()
        
        flash('Configuration mise à jour avec succès!', 'success')
        return redirect(url_for('admin.configuration'))
    
    return render_template('admin/config.html', form=form, config=config)

@admin.route('/messages')
@login_required
def messages():
    """Messages de contact"""
    messages = Contact.query.order_by(Contact.date_envoi.desc()).all()
    
    # Marquer tous les messages comme lus
    Contact.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    
    return render_template('admin/messages.html', messages=messages)

# Enregistrer le blueprint
app.register_blueprint(admin)
