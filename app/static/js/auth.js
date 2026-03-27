/**
 * auth.js - Animação de Background para Páginas de Autenticação
 * Versão: 3.2 - Corrigida e Melhorada
 */

(function() {
    'use strict';
    
    // Símbolos matemáticos
    var symbols = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        '+', '-', '×', '÷', '=', '≠', '≈', '±',
        '∑', '√', 'π', '∞', '∫', '∂', '∇',
        'α', 'β', 'γ', 'θ', 'λ', 'μ', 'σ',
        'x', 'y', 'z', 'a', 'b', 'c', 'n'
    ];
    
    // Função para número aleatório
    function rand(min, max) {
        return Math.random() * (max - min) + min;
    }
    
    // Função para item aleatório
    function randItem(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }
    
    // Injetar CSS de animação PRIMEIRO
    function injectCSS() {
        if (document.getElementById('animCSS')) return;
        
        var style = document.createElement('style');
        style.id = 'animCSS';
        style.textContent = [
            '/* Container de animação */',
            '.auth-bg {',
            '  position: fixed !important;',
            '  top: 0 !important;',
            '  left: 0 !important;',
            '  width: 100% !important;',
            '  height: 100% !important;',
            '  overflow: hidden !important;',
            '  z-index: 0 !important;',
            '  pointer-events: none !important;',
            '}',
            '',
            '/* Símbolos animados */',
            '.auth-symbol {',
            '  position: absolute;',
            '  color: rgba(255, 255, 255, 0.15);',
            '  font-family: "Times New Roman", Georgia, serif;',
            '  pointer-events: none;',
            '  user-select: none;',
            '  will-change: transform, opacity;',
            '  display: block;',
            '  line-height: 1;',
            '}',
            '',
            '/* Símbolos estáticos */',
            '.auth-symbol-static {',
            '  position: absolute;',
            '  color: rgba(255, 255, 255, 0.12);',
            '  font-family: "Times New Roman", Georgia, serif;',
            '  pointer-events: none;',
            '  user-select: none;',
            '  display: block;',
            '}',
            '',
            '/* Animação 1 */',
            '@keyframes symbolFloat1 {',
            '  0% {',
            '    transform: translate(0, 0) rotate(0deg);',
            '    opacity: 0;',
            '  }',
            '  10% {',
            '    opacity: var(--sym-opacity, 0.15);',
            '  }',
            '  50% {',
            '    transform: translate(calc(var(--drift-x, 20px) * 0.7), calc(var(--drift-y, -50vh) * 0.5)) rotate(calc(var(--rotation, 90deg) * 0.5));',
            '  }',
            '  90% {',
            '    opacity: var(--sym-opacity, 0.15);',
            '  }',
            '  100% {',
            '    transform: translate(var(--drift-x, 20px), var(--drift-y, -50vh)) rotate(var(--rotation, 90deg));',
            '    opacity: 0;',
            '  }',
            '}',
            '',
            '/* Animação 2 */',
            '@keyframes symbolFloat2 {',
            '  0% {',
            '    transform: translate(0, 0) rotate(0deg) scale(1);',
            '    opacity: 0;',
            '  }',
            '  15% {',
            '    opacity: var(--sym-opacity, 0.15);',
            '  }',
            '  33% {',
            '    transform: translate(calc(var(--drift-x, -20px) * 1.2), calc(var(--drift-y, -40vh) * 0.33)) rotate(calc(var(--rotation, -90deg) * 0.33)) scale(1.1);',
            '  }',
            '  66% {',
            '    transform: translate(calc(var(--drift-x, -20px) * 0.4), calc(var(--drift-y, -40vh) * 0.66)) rotate(calc(var(--rotation, -90deg) * 0.66)) scale(0.9);',
            '  }',
            '  85% {',
            '    opacity: var(--sym-opacity, 0.15);',
            '  }',
            '  100% {',
            '    transform: translate(calc(var(--drift-x, -20px) * -0.3), var(--drift-y, -40vh)) rotate(var(--rotation, -90deg)) scale(1);',
            '    opacity: 0;',
            '  }',
            '}',
            '',
            '/* Animação 3 */',
            '@keyframes symbolFloat3 {',
            '  0% {',
            '    transform: translate(0, 0) rotate(0deg);',
            '    opacity: 0;',
            '  }',
            '  12% {',
            '    opacity: var(--sym-opacity, 0.15);',
            '  }',
            '  25% {',
            '    transform: translate(calc(var(--drift-x, 25px) * -0.5), calc(var(--drift-y, -60vh) * 0.25)) rotate(calc(var(--rotation, 120deg) * 0.25));',
            '  }',
            '  50% {',
            '    transform: translate(calc(var(--drift-x, 25px) * 0.8), calc(var(--drift-y, -60vh) * 0.5)) rotate(calc(var(--rotation, 120deg) * 0.5));',
            '  }',
            '  75% {',
            '    transform: translate(calc(var(--drift-x, 25px) * 0.2), calc(var(--drift-y, -60vh) * 0.75)) rotate(calc(var(--rotation, 120deg) * 0.75));',
            '  }',
            '  88% {',
            '    opacity: var(--sym-opacity, 0.15);',
            '  }',
            '  100% {',
            '    transform: translate(calc(var(--drift-x, 25px) * -0.4), var(--drift-y, -60vh)) rotate(var(--rotation, 120deg));',
            '    opacity: 0;',
            '  }',
            '}',
            '',
            '/* Tema escuro */',
            '[data-theme="dark"] .auth-symbol {',
            '  color: rgba(255, 255, 255, 0.1);',
            '}',
            '',
            '[data-theme="dark"] .auth-symbol-static {',
            '  color: rgba(255, 255, 255, 0.08);',
            '}',
            '',
            '/* Movimento reduzido */',
            '@media (prefers-reduced-motion: reduce) {',
            '  .auth-symbol {',
            '    animation: none !important;',
            '    opacity: 0.1 !important;',
            '  }',
            '}'
        ].join('\n');
        
        document.head.appendChild(style);
    }
    
    // Criar um símbolo
    function createSymbol(container) {
        var el = document.createElement('span');
        el.className = 'auth-symbol';
        el.textContent = randItem(symbols);
        
        // Posição aleatória
        var x = rand(5, 95);
        var y = rand(5, 95);
        var size = rand(1.0, 2.8);
        var opacity = rand(0.08, 0.18);
        var duration = rand(15, 30);
        var delay = rand(0, 12);
        var driftX = rand(-60, 60);
        var driftY = rand(-100, -180);
        var rotation = rand(-180, 180);
        
        // Aplicar estilos inline
        el.style.left = x + '%';
        el.style.top = y + '%';
        el.style.fontSize = size + 'rem';
        el.style.setProperty('--drift-x', driftX + 'px');
        el.style.setProperty('--drift-y', driftY + 'vh');
        el.style.setProperty('--rotation', rotation + 'deg');
        el.style.setProperty('--sym-opacity', opacity);
        
        // Escolher animação aleatoriamente
        var anims = ['symbolFloat1', 'symbolFloat2', 'symbolFloat3'];
        el.style.animation = randItem(anims) + ' ' + duration + 's ease-in-out ' + delay + 's infinite';
        
        container.appendChild(el);
        return el;
    }
    
    // Inicializar animação de background
    function initAnimation() {
        var bg = document.getElementById('authBg');
        if (!bg) {
            console.warn('Container authBg não encontrado');
            return;
        }
        
        // Limpar conteúdo existente
        bg.innerHTML = '';
        
        // Verificar preferência de movimento reduzido
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            // Criar símbolos estáticos
            for (var i = 0; i < 25; i++) {
                var el = document.createElement('span');
                el.className = 'auth-symbol-static';
                el.textContent = randItem(symbols);
                el.style.left = rand(5, 95) + '%';
                el.style.top = rand(5, 95) + '%';
                el.style.fontSize = rand(1.0, 2.5) + 'rem';
                el.style.opacity = rand(0.08, 0.15);
                bg.appendChild(el);
            }
            return;
        }
        
        // Criar símbolos animados
        var count = window.innerWidth < 768 ? 35 : 50;
        for (var i = 0; i < count; i++) {
            createSymbol(bg);
        }
    }
    
    // Toggle de senha
    function initPasswordToggle() {
        document.querySelectorAll('.auth-password-toggle').forEach(function(btn) {
            var input = btn.previousElementSibling;
            if (!input) return;
            
            btn.addEventListener('click', function() {
                var isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                var icon = this.querySelector('i');
                if (icon) {
                    icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
                }
                input.focus();
            });
        });
    }
    
    // Animação de entrada do wrapper
    function initEntryAnimation() {
        var wrapper = document.querySelector('.auth-wrapper');
        if (wrapper) {
            wrapper.style.opacity = '0';
            wrapper.style.transform = 'scale(0.95) translateY(20px)';
            
            setTimeout(function() {
                wrapper.style.transition = 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
                wrapper.style.opacity = '1';
                wrapper.style.transform = 'scale(1) translateY(0)';
            }, 100);
        }
    }
    
    // Pausar animações quando aba não visível
    function initVisibilityHandler() {
        document.addEventListener('visibilitychange', function() {
            var syms = document.querySelectorAll('.auth-symbol');
            var state = document.hidden ? 'paused' : 'running';
            for (var i = 0; i < syms.length; i++) {
                syms[i].style.animationPlayState = state;
            }
        });
    }
    
    // Inicialização principal
    function init() {
        injectCSS();
        initAnimation();
        initPasswordToggle();
        initEntryAnimation();
        initVisibilityHandler();
    }
    
    // Executar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // API pública para debug
    window.AuthAnimation = {
        refresh: initAnimation,
        getCount: function() {
            return document.querySelectorAll('.auth-symbol').length;
        }
    };
    
})();
