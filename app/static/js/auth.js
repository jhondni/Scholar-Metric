/**
 * auth.js - JavaScript compartilhado para páginas de autenticação
 * Login, Registro e Recuperação de Senha
 */

(function() {
    'use strict';
    
    // Símbolos para animação de fundo
    const SYMBOLS = {
        math: [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            '+', '−', '×', '÷', '∑', '√', 'π', '∞', 'Δ', 'θ',
            '∫', '≈', '≠', '±', 'μ', 'σ', 'λ', 'α', 'β', 'γ',
            '∂', '∇', '∈', '∉', '⊂', '⊃', '∪', '∩', '∀', '∃',
            '=', '<', '>'
        ],
        simple: ['?', '!', '@', '#', '%', '&', '*', '+', '-', '=']
    };
    
    /**
     * Inicializa animação de símbolos no background
     */
    function initBackgroundAnimation() {
        const bg = document.getElementById('authBg');
        if (!bg) return;
        
        // Determinar tipo de símbolos baseado na página
        const isLoginPage = document.querySelector('.auth-test');
        const symbols = isLoginPage ? SYMBOLS.math : SYMBOLS.simple;
        const totalSymbols = 45;
        
        for (let i = 0; i < totalSymbols; i++) {
            const symbol = document.createElement('span');
            symbol.className = 'auth-symbol';
            symbol.textContent = symbols[Math.floor(Math.random() * symbols.length)];
            
            // Posição e animação aleatórias
            symbol.style.left = Math.random() * 100 + '%';
            symbol.style.fontSize = (Math.random() * 2.5 + 0.8) + 'rem';
            symbol.style.animationDuration = (Math.random() * 25 + 20) + 's';
            symbol.style.animationDelay = (Math.random() * 30) + 's';
            
            bg.appendChild(symbol);
        }
    }
    
    /**
     * Inicializa toggle de visibilidade da senha
     */
    function initPasswordToggle() {
        const toggleBtns = document.querySelectorAll('.auth-password-toggle');
        
        toggleBtns.forEach(btn => {
            const input = btn.previousElementSibling;
            if (!input) return;
            
            btn.addEventListener('click', function() {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                
                const icon = this.querySelector('i');
                if (icon) {
                    icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
                }
            });
        });
    }
    
    /**
     * Inicializa validação visual de formulários
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('.auth-form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('.auth-input[required]');
            
            inputs.forEach(input => {
                // Remover erro ao digitar
                input.addEventListener('input', function() {
                    this.classList.remove('auth-input-error');
                    const errorMsg = this.parentElement.querySelector('.auth-error');
                    if (errorMsg) errorMsg.style.display = 'none';
                });
                
                // Validação ao perder foco
                input.addEventListener('blur', function() {
                    if (!this.value.trim() && this.required) {
                        this.classList.add('auth-input-error');
                    }
                });
            });
        });
    }
    
    /**
     * Inicializa animações de entrada
     */
    function initEntryAnimations() {
        const wrapper = document.querySelector('.auth-wrapper');
        if (wrapper) {
            wrapper.style.opacity = '0';
            wrapper.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                wrapper.style.transition = 'all 0.5s ease';
                wrapper.style.opacity = '1';
                wrapper.style.transform = 'scale(1)';
            }, 100);
        }
    }
    
    /**
     * Inicializa todos os componentes
     */
    function init() {
        initBackgroundAnimation();
        initPasswordToggle();
        initFormValidation();
        initEntryAnimations();
    }
    
    // Executar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
