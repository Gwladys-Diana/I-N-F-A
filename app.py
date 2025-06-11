import os
import logging
import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier .env
load_dotenv()

# Utiliser pymysql comme moteur MySQL
pymysql.install_as_MySQLdb()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Créer l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "secret_key_default")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# -----------------------------------------
# CONFIGURATION DE LA BASE DE DONNÉES
# -----------------------------------------

# ⛔️ Configuration MySQL (commentée pour usage PostgreSQL)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
#     "DATABASE_URL", 
#     "mysql+pymysql://root@localhost/infa_base_deploye"
# )

# ✅ Configuration PostgreSQL (Render ou local)
# Exemple : postgresql://user:password@host:port/dbname
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", 
    "postgresql://infa:APf50FwTxkydOfhGwj1X9rUQaODWImGP@dpg-d14ptcgdl3ps738hb8rg-a.oregon-postgres.render.com/infa_de_tove"
)

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# -----------------------------------------
# CONFIGURATION DES FICHIERS À TÉLÉCHARGER
# -----------------------------------------

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

# Initialiser SQLAlchemy avec l'app
db.init_app(app)

# Configurer Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import Admin
    return Admin.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Créer le dossier d’upload si nécessaire
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    import models
    db.create_all()

    # Créer un compte admin si aucun n’existe
    from models import Admin
    from werkzeug.security import generate_password_hash

    if not Admin.query.first():
        admin = Admin(
            username='admin',
            email='admin@infa-tove.org',
            password_hash=generate_password_hash('admin123'),
            nom='Administrateur',
            prenom='Principal'
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("✅ Utilisateur admin créé : admin/admin123")
