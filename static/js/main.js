// Main JavaScript pour l'interface publique INFA
document.addEventListener('DOMContentLoaded', function() {
    console.log('INFA - Interface publique chargée');
    
    // Initialisation
    initializeComponents();
    initializeAnimations();
    initializeForms();
    initializeModals();
    initializeSearch();
});

// Initialisation des composants
function initializeComponents() {
    // Smooth scrolling pour les liens d'ancrage
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }
    });
    
    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
    }
    
    // Fermer le menu mobile lors du clic sur un lien
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                navbarCollapse.classList.remove('show');
            }
        });
    });
}

// Animations d'apparition
function initializeAnimations() {
    // Observer pour les animations au scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observer les éléments à animer
    document.querySelectorAll('.card, .formation-card, .actualite-card, .membre-card').forEach(el => {
        observer.observe(el);
    });
    
    // Animation des compteurs (si présents)
    animateCounters();
}

// Animation des compteurs
function animateCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-counter'));
        const duration = 2000; // 2 secondes
        const step = target / (duration / 16); // 60 FPS
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        // Observer pour démarrer l'animation
        const counterObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    counterObserver.unobserve(entry.target);
                }
            });
        });
        
        counterObserver.observe(counter);
    });
}

// Initialisation des formulaires
function initializeForms() {
    // Validation en temps réel
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
        
        // Soumission du formulaire
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Veuillez corriger les erreurs dans le formulaire.', 'danger');
                
                // Scroll vers le premier champ invalide
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
            } else {
                showLoadingButton(form.querySelector('button[type="submit"]'));
            }
        });
    });
    
    // Upload de fichiers avec preview
    initializeFileUploads();
}

// Validation des champs
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const required = field.hasAttribute('required');
    let isValid = true;
    let message = '';
    
    // Supprimer les anciens messages
    removeFieldError(field);
    
    // Champ requis
    if (required && !value) {
        isValid = false;
        message = 'Ce champ est obligatoire.';
    }
    
    // Validation par type
    if (value && isValid) {
        switch (type) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    isValid = false;
                    message = 'Veuillez saisir une adresse email valide.';
                }
                break;
                
            case 'tel':
                const phoneRegex = /^(\+228|00228|228)?[0-9]{8}$/;
                if (!phoneRegex.test(value.replace(/[\s-]/g, ''))) {
                    isValid = false;
                    message = 'Veuillez saisir un numéro de téléphone valide.';
                }
                break;
                
            case 'date':
                const date = new Date(value);
                const today = new Date();
                if (field.name === 'date_naissance' && date > today) {
                    isValid = false;
                    message = 'La date de naissance ne peut pas être dans le futur.';
                }
                break;
        }
    }
    
    // Validation de longueur
    if (value && isValid) {
        const minLength = field.getAttribute('minlength');
        const maxLength = field.getAttribute('maxlength');
        
        if (minLength && value.length < parseInt(minLength)) {
            isValid = false;
            message = `Ce champ doit contenir au moins ${minLength} caractères.`;
        }
        
        if (maxLength && value.length > parseInt(maxLength)) {
            isValid = false;
            message = `Ce champ ne peut pas dépasser ${maxLength} caractères.`;
        }
    }
    
    // Appliquer les classes CSS
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field, message);
    }
    
    return isValid;
}

// Affichage des erreurs de champ
function showFieldError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Suppression des erreurs de champ
function removeFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

// Upload de fichiers
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            handleFileUpload(this);
        });
        
        // Drag & Drop
        const parent = input.closest('.file-upload') || input.parentNode;
        
        parent.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        parent.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        parent.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                handleFileUpload(input);
            }
        });
    });
}

// Gestion de l'upload de fichier
function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    // Validation de la taille (16MB max)
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showAlert('Le fichier est trop volumineux. Taille maximum: 16MB.', 'danger');
        input.value = '';
        return;
    }
    
    // Validation du type
    const allowedTypes = {
        'cv': ['application/pdf'],
        'diplome': ['application/pdf'],
        'photo': ['image/jpeg', 'image/png', 'image/jpg']
    };
    
    const inputName = input.name;
    if (allowedTypes[inputName] && !allowedTypes[inputName].includes(file.type)) {
        const typeNames = {
            'application/pdf': 'PDF',
            'image/jpeg': 'JPG',
            'image/png': 'PNG',
            'image/jpg': 'JPG'
        };
        
        const allowed = allowedTypes[inputName].map(type => typeNames[type]).join(', ');
        showAlert(`Type de fichier non autorisé. Types acceptés: ${allowed}`, 'danger');
        input.value = '';
        return;
    }
    
    // Affichage du nom du fichier
    const label = input.closest('.file-upload')?.querySelector('.file-upload-label');
    if (label) {
        label.innerHTML = `
            <i class="fas fa-file-check text-success"></i>
            <span class="ms-2">${file.name}</span>
            <small class="d-block text-muted mt-1">${formatFileSize(file.size)}</small>
        `;
    }
    
    // Preview pour les images
    if (file.type.startsWith('image/')) {
        createImagePreview(input, file);
    }
}

// Création d'un aperçu d'image
function createImagePreview(input, file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        let preview = input.parentNode.querySelector('.image-preview');
        
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'image-preview mt-2';
            input.parentNode.appendChild(preview);
        }
        
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Aperçu" class="img-thumbnail" style="max-width: 150px; max-height: 150px;">
        `;
    };
    
    reader.readAsDataURL(file);
}

// Formatage de la taille de fichier
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Initialisation des modales
function initializeModals() {
    // Fermeture des modales
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal') || e.target.classList.contains('modal-close')) {
            const modal = e.target.closest('.modal');
            if (modal) {
                closeModal(modal);
            }
        }
    });
    
    // Fermeture par échap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

// Ouverture de modale
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Focus sur le premier élément focusable
        const focusable = modal.querySelector('input, button, textarea, select');
        if (focusable) {
            setTimeout(() => focusable.focus(), 100);
        }
    }
}

// Fermeture de modale
function closeModal(modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
}

// Initialisation de la recherche
function initializeSearch() {
    const searchForms = document.querySelectorAll('.search-form');
    
    searchForms.forEach(form => {
        const input = form.querySelector('input[type="search"]');
        
        if (input) {
            // Recherche en temps réel avec debounce
            let timeout;
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    if (this.value.length >= 3 || this.value.length === 0) {
                        performSearch(this.value);
                    }
                }, 300);
            });
        }
    });
}

// Exécution de la recherche
function performSearch(query) {
    // Cette fonction peut être étendue pour faire de la recherche AJAX
    console.log('Recherche:', query);
}

// Affichage des alertes
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = getOrCreateAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Suppression automatique
    if (duration > 0) {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, duration);
    }
    
    // Animation d'entrée
    setTimeout(() => alert.classList.add('show'), 10);
}

// Conteneur d'alertes
function getOrCreateAlertContainer() {
    let container = document.getElementById('alert-container');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'alert-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    return container;
}

// Animation du bouton de chargement
function showLoadingButton(button) {
    if (!button) return;
    
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        Traitement...
    `;
    
    // Restaurer après 10 secondes max
    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = originalText;
    }, 10000);
}

// Confirmation d'action
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Utilitaires pour les dates
function formatDate(dateString, locale = 'fr-FR') {
    const date = new Date(dateString);
    return date.toLocaleDateString(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Scroll vers le haut
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Bouton retour en haut
document.addEventListener('scroll', function() {
    const backToTopButton = document.getElementById('back-to-top');
    
    if (window.scrollY > 300) {
        if (backToTopButton) {
            backToTopButton.style.display = 'block';
        } else {
            createBackToTopButton();
        }
    } else if (backToTopButton) {
        backToTopButton.style.display = 'none';
    }
});

// Création du bouton retour en haut
function createBackToTopButton() {
    const button = document.createElement('button');
    button.id = 'back-to-top';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--secondary-green) 0%, var(--primary-green) 100%);
        color: white;
        border: none;
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    
    button.addEventListener('click', scrollToTop);
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
    });
    button.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });
    
    document.body.appendChild(button);
}

// Lazy loading pour les images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialisation du lazy loading au chargement
document.addEventListener('DOMContentLoaded', initializeLazyLoading);

// Export des fonctions utiles
window.INFA = {
    showAlert,
    openModal,
    closeModal,
    confirmAction,
    formatDate,
    scrollToTop,
    validateField,
    showLoadingButton
};

console.log('INFA - Scripts publics initialisés');
