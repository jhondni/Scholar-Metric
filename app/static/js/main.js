/**
 * main.js - JavaScript principal do Analitcs School
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initSidebar();
    initAlerts();
    initModals();
    initDropdowns();
    initTooltips();
});

/**
 * Sidebar - Toggle e comportamento mobile
 */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    // Criar overlay para mobile
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }
    
    overlay.addEventListener('click', function() {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    });
    
    // Fechar sidebar ao clicar em link (mobile)
    const navLinks = sidebar.querySelectorAll('.nav-item a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 1200) {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
        });
    });
}

/**
 * Alertas - Fechar automaticamente
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            });
        }
        
        // Auto-fechar após 5 segundos
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

/**
 * Modais
 */
function initModals() {
    // Abrir modal
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = this.getAttribute('data-modal');
            openModal(modalId);
        });
    });
    
    // Fechar modal
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
    
    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            closeModal(modal.id);
        });
    });
    
    // Fechar com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal-overlay.active');
            if (activeModal) {
                closeModal(activeModal.id);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/**
 * Dropdowns
 */
function initDropdowns() {
    document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.nextElementSibling;
            dropdown.classList.toggle('active');
        });
    });
    
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-menu.active').forEach(menu => {
            menu.classList.remove('active');
        });
    });
}

/**
 * Tooltips
 */
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const text = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = text;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            tooltip.style.left = rect.left + (rect.width - tooltip.offsetWidth) / 2 + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

/**
 * Confirmação de exclusão
 */
function confirmDelete(message, callback) {
    if (confirm(message || 'Tem certeza que deseja excluir este item?')) {
        callback();
    }
}

/**
 * Loading state em botões
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
    }
}

/**
 * Formatação de dados
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

function formatDateTime(date) {
    return new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'short'
    }).format(new Date(date));
}

/**
 * Validação de formulários
 */
function validateForm(form) {
    let isValid = true;
    
    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
            
            // Adicionar mensagem de erro
            let errorMsg = field.parentNode.querySelector('.form-error');
            if (!errorMsg) {
                errorMsg = document.createElement('span');
                errorMsg.className = 'form-error';
                field.parentNode.appendChild(errorMsg);
            }
            errorMsg.textContent = 'Este campo é obrigatório';
        } else {
            field.classList.remove('error');
            const errorMsg = field.parentNode.querySelector('.form-error');
            if (errorMsg) errorMsg.remove();
        }
    });
    
    return isValid;
}

/**
 * Debounce para otimização
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Animação de fadeOut
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);
