import os
import uuid
from PIL import Image
from flask import current_app
import secrets

def generate_filename(original_filename, prefix=""):
    """Génère un nom de fichier unique"""
    if original_filename:
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{prefix}_{secrets.token_hex(8)}.{extension}"
        return unique_filename
    return None

def save_uploaded_file(file, folder, prefix=""):
    """Sauvegarde un fichier uploadé avec un nom unique"""
    if file and file.filename:
        filename = generate_filename(file.filename, prefix)
        
        # Pour les uploads dans static/uploads/
        upload_dir = os.path.join(current_app.root_path, 'static', folder)
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        return filename
    return None

def resize_image(image_path, max_width=800, max_height=600, quality=85):
    """Redimensionne une image pour optimiser l'espace de stockage"""
    try:
        with Image.open(image_path) as img:
            # Convertir en RGB si nécessaire
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensionner en gardant les proportions
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Sauvegarder avec compression
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            
    except Exception as e:
        current_app.logger.error(f"Erreur lors du redimensionnement de l'image: {e}")

def allowed_file(filename, allowed_extensions=None):
    """Vérifie si l'extension du fichier est autorisée"""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def format_date_fr(date):
    """Formate une date en français"""
    if date:
        mois = [
            'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
        ]
        return f"{date.day} {mois[date.month - 1]} {date.year}"
    return ""

def format_file_size(size_bytes):
    """Formate la taille d'un fichier en unités lisibles"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text, max_length=150):
    """Tronque un texte à une longueur donnée"""
    if text and len(text) > max_length:
        return text[:max_length].rsplit(' ', 1)[0] + '...'
    return text or ""

def validate_phone_number(phone):
    """Valide un numéro de téléphone"""
    # Logique de validation simple pour les numéros togolais
    import re
    pattern = r'^(\+228|00228|228)?[0-9]{8}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', ''))

def get_file_extension(filename):
    """Récupère l'extension d'un fichier"""
    if filename and '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None

def is_safe_url(target):
    """Vérifie si une URL est sûre pour la redirection"""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def generate_numero_dossier(year=None):
    """Génère un numéro de dossier unique"""
    if year is None:
        from datetime import datetime
        year = datetime.now().year
    
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"INFA{year}{unique_id}"

# Filtres personnalisés pour Jinja2
def init_template_filters(app):
    """Initialise les filtres personnalisés pour les templates"""
    
    @app.template_filter('date_fr')
    def date_fr_filter(date):
        return format_date_fr(date)
    
    @app.template_filter('truncate_text')
    def truncate_text_filter(text, length=150):
        return truncate_text(text, length)
    
    @app.template_filter('file_size')
    def file_size_filter(size):
        return format_file_size(size)

# Fonction utilitaire pour les statistiques
def calculate_statistics():
    """Calcule diverses statistiques pour le tableau de bord"""
    from models import Candidature, Formation
    from sqlalchemy import func
    
    stats = {}
    
    # Statistiques générales
    stats['total_candidatures'] = Candidature.query.count()
    stats['candidatures_en_attente'] = Candidature.query.filter_by(statut='En attente').count()
    stats['candidatures_acceptees'] = Candidature.query.filter_by(statut='Accepté').count()
    stats['candidatures_rejetees'] = Candidature.query.filter_by(statut='Rejeté').count()
    
    # Taux d'acceptation
    if stats['total_candidatures'] > 0:
        stats['taux_acceptation'] = round(
            (stats['candidatures_acceptees'] / stats['total_candidatures']) * 100, 1
        )
    else:
        stats['taux_acceptation'] = 0
    
    return stats
