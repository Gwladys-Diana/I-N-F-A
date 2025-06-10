// JavaScript pour l'interface d'administration INFA
document.addEventListener('DOMContentLoaded', function() {
    console.log('INFA - Interface admin chargée');
    
    // Initialisation des composants admin
    initializeSidebar();
    initializeCharts();
    initializeDataTables();
    initializeForms();
    initializeModals();
    initializeTooltips();
    initializeFileUploads();
});

// Initialisation de la sidebar
function initializeSidebar() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.admin-sidebar');
    const mainContent = document.querySelector('.admin-main');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Sauvegarder l'état dans localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
        
        // Restaurer l'état de la sidebar
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
        }
    }
    
    // Menu actif
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Responsive sidebar
    handleResponsiveSidebar();
    window.addEventListener('resize', handleResponsiveSidebar);
}

// Gestion responsive de la sidebar
function handleResponsiveSidebar() {
    const sidebar = document.querySelector('.admin-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (window.innerWidth <= 992) {
        sidebar.classList.add('mobile');
        
        // Créer l'overlay si nécessaire
        if (!overlay) {
            const newOverlay = document.createElement('div');
            newOverlay.className = 'sidebar-overlay';
            newOverlay.addEventListener('click', () => {
                sidebar.classList.remove('show');
                newOverlay.classList.remove('show');
            });
            document.body.appendChild(newOverlay);
        }
        
        // Toggle mobile
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            document.querySelector('.sidebar-overlay').classList.toggle('show');
        });
    } else {
        sidebar.classList.remove('mobile', 'show');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }
}

// Initialisation des graphiques
function initializeCharts() {
    // Graphique des candidatures par mois
    const monthlyChart = document.getElementById('monthlyChart');
    if (monthlyChart && typeof Chart !== 'undefined') {
        const ctx = monthlyChart.getContext('2d');
        
        // Récupérer les données depuis les attributs data-*
        const labels = JSON.parse(monthlyChart.dataset.labels || '[]');
        const data = JSON.parse(monthlyChart.dataset.data || '[]');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Candidatures',
                    data: data,
                    borderColor: '#4a7c59',
                    backgroundColor: 'rgba(74, 124, 89, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    // Graphique en secteurs des formations
    const formationsChart = document.getElementById('formationsChart');
    if (formationsChart && typeof Chart !== 'undefined') {
        const ctx = formationsChart.getContext('2d');
        
        const labels = JSON.parse(formationsChart.dataset.labels || '[]');
        const data = JSON.parse(formationsChart.dataset.data || '[]');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#2d5a27',
                        '#4a7c59',
                        '#8fbc8f',
                        '#90c695',
                        '#a8d5a8',
                        '#c0e4c0'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Initialisation des DataTables
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        if (typeof $ !== 'undefined' && $.fn.DataTable) {
            $(table).DataTable({
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.11.5/i18n/fr-FR.json'
                },
                responsive: true,
                pageLength: 25,
                order: [[0, 'desc']],
                columnDefs: [
                    {
                        targets: 'no-sort',
                        orderable: false
                    }
                ]
            });
        }
    });
}

// Initialisation des formulaires admin
function initializeForms() {
    const forms = document.querySelectorAll('.admin-form');
    
    forms.forEach(form => {
        // Validation en temps réel
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateAdminField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateAdminField(this);
                }
            });
        });
        
        // Soumission du formulaire
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateAdminField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAdminAlert('Veuillez corriger les erreurs dans le formulaire.', 'danger');
                
                // Scroll vers le premier champ invalide
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
            } else {
                showLoadingState(form.querySelector('button[type="submit"]'));
            }
        });
    });
    
    // Auto-save pour les brouillons
    initializeAutoSave();
}

// Validation des champs admin
function validateAdminField(field) {
    const value = field.value.trim();
    const required = field.hasAttribute('required');
    let isValid = true;
    let message = '';
    
    // Supprimer les anciens messages
    removeAdminFieldError(field);
    
    // Champ requis
    if (required && !value) {
        isValid = false;
        message = 'Ce champ est obligatoire.';
    }
    
    // Validation spécifique
    if (value && isValid) {
        switch (field.type) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    isValid = false;
                    message = 'Adresse email invalide.';
                }
                break;
                
            case 'url':
                try {
                    new URL(value);
                } catch {
                    isValid = false;
                    message = 'URL invalide.';
                }
                break;
                
            case 'number':
                if (isNaN(value) || value < 0) {
                    isValid = false;
                    message = 'Nombre invalide.';
                }
                break;
        }
    }
    
    // Appliquer les classes
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showAdminFieldError(field, message);
    }
    
    return isValid;
}

// Affichage des erreurs de champ admin
function showAdminFieldError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback-admin';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Suppression des erreurs de champ admin
function removeAdminFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback-admin');
    if (existingError) {
        existingError.remove();
    }
}

// Auto-sauvegarde
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    
    autoSaveForms.forEach(form => {
        const formId = form.id || 'auto-save-form';
        let saveTimeout;
        
        // Restaurer les données sauvegardées
        restoreFormData(form, formId);
        
        // Sauvegarder lors des changements
        form.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                saveFormData(form, formId);
                showAutoSaveIndicator();
            }, 2000);
        });
        
        // Nettoyer lors de la soumission réussie
        form.addEventListener('submit', function() {
            localStorage.removeItem(`autosave_${formId}`);
        });
    });
}

// Sauvegarde des données de formulaire
function saveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
}

// Restauration des données de formulaire
function restoreFormData(form, formId) {
    const savedData = localStorage.getItem(`autosave_${formId}`);
    
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && field.type !== 'file') {
                    field.value = data[key];
                }
            });
            
            showAutoSaveIndicator('Brouillon restauré');
        } catch (e) {
            console.error('Erreur lors de la restauration:', e);
        }
    }
}

// Indicateur d'auto-sauvegarde
function showAutoSaveIndicator(message = 'Brouillon sauvegardé') {
    let indicator = document.getElementById('auto-save-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'auto-save-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-size: 0.875rem;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(indicator);
    }
    
    indicator.textContent = message;
    indicator.style.opacity = '1';
    
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

// Initialisation des modales admin
function initializeModals() {
    // Ouverture des modales
    document.addEventListener('click', function(e) {
        const trigger = e.target.closest('[data-modal]');
        if (trigger) {
            e.preventDefault();
            const modalId = trigger.dataset.modal;
            openAdminModal(modalId);
        }
    });
    
    // Fermeture des modales
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-admin') || e.target.classList.contains('modal-close')) {
            const modal = e.target.closest('.modal-admin');
            if (modal) {
                closeAdminModal(modal);
            }
        }
    });
    
    // Fermeture par échap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal-admin.show');
            if (openModal) {
                closeAdminModal(openModal);
            }
        }
    });
}

// Ouverture de modale admin
function openAdminModal(modalId) {
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

// Fermeture de modale admin
function closeAdminModal(modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';
}

// Initialisation des tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.dataset.tooltip);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

// Affichage de tooltip
function showTooltip(element, text) {
    let tooltip = document.getElementById('admin-tooltip');
    
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.id = 'admin-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background: #333;
            color: white;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.875rem;
            z-index: 10000;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(tooltip);
    }
    
    tooltip.textContent = text;
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    tooltip.style.opacity = '1';
}

// Masquage de tooltip
function hideTooltip() {
    const tooltip = document.getElementById('admin-tooltip');
    if (tooltip) {
        tooltip.style.opacity = '0';
    }
}

// Upload de fichiers admin
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('.admin-file-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            handleAdminFileUpload(this);
        });
    });
}

// Gestion de l'upload admin
function handleAdminFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    // Validation de la taille
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showAdminAlert('Fichier trop volumineux (max 16MB)', 'danger');
        input.value = '';
        return;
    }
    
    // Preview
    const preview = input.parentNode.querySelector('.file-preview');
    if (preview) {
        preview.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-file text-primary me-2"></i>
                <div>
                    <div class="fw-bold">${file.name}</div>
                    <small class="text-muted">${formatFileSize(file.size)}</small>
                </div>
            </div>
        `;
    }
}

// Formatage de taille de fichier
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Alertes admin
function showAdminAlert(message, type = 'info', duration = 5000) {
    const alertContainer = getOrCreateAdminAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert-admin alert-admin-${type}`;
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
}

// Conteneur d'alertes admin
function getOrCreateAdminAlertContainer() {
    let container = document.getElementById('admin-alert-container');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'admin-alert-container';
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

// État de chargement
function showLoadingState(button) {
    if (!button) return;
    
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `
        <span class="loading-spinner me-2"></span>
        Traitement...
    `;
    
    // Restaurer après 10 secondes
    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = originalText;
    }, 10000);
}

// Confirmation d'action
function confirmAdminAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Suppression d'élément avec confirmation
function deleteItem(url, itemName) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer ${itemName} ?`)) {
        // Créer un formulaire caché pour la suppression
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        
        // Ajouter le token CSRF si disponible
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = csrfToken.content;
            form.appendChild(input);
        }
        
        document.body.appendChild(form);
        form.submit();
    }
}

// Filtres de tableau
function initializeTableFilters() {
    const filterInputs = document.querySelectorAll('[data-filter]');
    
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            const filterValue = this.value.toLowerCase();
            const targetTable = document.querySelector(this.dataset.filter);
            
            if (targetTable) {
                const rows = targetTable.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(filterValue) ? '' : 'none';
                });
            }
        });
    });
}

// Tri de tableau
function sortTable(table, column, direction = 'asc') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        
        if (direction === 'asc') {
            return aVal.localeCompare(bVal);
        } else {
            return bVal.localeCompare(aVal);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// Export de données
function exportTableData(tableId, filename = 'export') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csvContent = Array.from(rows).map(row => {
        const cells = row.querySelectorAll('td, th');
        return Array.from(cells).map(cell => {
            return `"${cell.textContent.trim().replace(/"/g, '""')}"`;
        }).join(',');
    }).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `${filename}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Statistiques en temps réel
function updateStats() {
    fetch('/admin/api/stats')
        .then(response => response.json())
        .then(data => {
            // Mettre à jour les cartes de statistiques
            Object.keys(data).forEach(key => {
                const element = document.getElementById(`stat-${key}`);
                if (element) {
                    element.textContent = data[key];
                }
            });
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour des stats:', error);
        });
}

// Recherche globale
function initializeGlobalSearch() {
    const searchInput = document.getElementById('global-search');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                
                if (query.length >= 3) {
                    performGlobalSearch(query);
                } else {
                    clearSearchResults();
                }
            }, 300);
        });
    }
}

// Exécution de la recherche globale
function performGlobalSearch(query) {
    // Ici, vous pourriez implémenter une recherche AJAX
    console.log('Recherche globale:', query);
}

// Nettoyage des résultats de recherche
function clearSearchResults() {
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = '';
    }
}

// Gestion des notifications
function showNotification(message, type = 'info') {
    // Créer une notification toast
    const notification = document.createElement('div');
    notification.className = `notification toast-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)} me-2"></i>
            ${message}
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    // Styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-left: 4px solid ${getNotificationColor(type)};
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 4px;
        padding: 1rem;
        max-width: 350px;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animation d'entrée
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Fermeture
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto-suppression
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Icônes de notification
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        warning: 'exclamation-triangle',
        danger: 'times-circle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

// Couleurs de notification
function getNotificationColor(type) {
    const colors = {
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8'
    };
    return colors[type] || colors.info;
}

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', function() {
    initializeTableFilters();
    initializeGlobalSearch();
    
    // Mettre à jour les stats toutes les 30 secondes
    setInterval(updateStats, 30000);
});

// Export des fonctions utiles
window.AdminINFA = {
    showAdminAlert,
    openAdminModal,
    closeAdminModal,
    confirmAdminAction,
    deleteItem,
    showNotification,
    exportTableData,
    showLoadingState
};

console.log('INFA - Scripts admin initialisés');
