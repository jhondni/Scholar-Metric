/**
 * theme.js - Gerenciamento de tema claro/escuro do Analitcs School
 */

(function() {
    'use strict';
    
    const THEME_KEY = 'analitcs_theme';
    const THEMES = {
        LIGHT: 'light',
        DARK: 'dark'
    };
    
    /**
     * Inicializa o tema
     */
    function initTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Prioridade: 1. Salvo, 2. Preferência do sistema, 3. Padrão (light)
        const theme = savedTheme || (prefersDark ? THEMES.DARK : THEMES.LIGHT);
        setTheme(theme);
        
        // Listener para mudanças na preferência do sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(THEME_KEY)) {
                setTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
            }
        });
    }
    
    /**
     * Define o tema
     */
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
        updateToggleButton(theme);
        
        // Salvar no servidor se autenticado
        saveThemeToServer(theme);
    }
    
    /**
     * Alterna entre temas
     */
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
        setTheme(newTheme);
    }
    
    /**
     * Atualiza o botão de toggle
     */
    function updateToggleButton(theme) {
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.className = theme === THEMES.DARK ? 'fas fa-sun' : 'fas fa-moon';
            }
            toggleBtn.setAttribute('title', 
                theme === THEMES.DARK ? 'Modo claro' : 'Modo escuro'
            );
        }
    }
    
    /**
     * Salva preferência no servidor
     */
    async function saveThemeToServer(theme) {
        try {
            await fetch('/configuracoes/tema', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tema: theme })
            });
        } catch (error) {
            // Falha silenciosa - tema já está salvo no localStorage
            console.debug('Não foi possível salvar tema no servidor:', error);
        }
    }
    
    /**
     * Retorna o tema atual
     */
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme');
    }
    
    // Event listeners
    document.addEventListener('DOMContentLoaded', function() {
        initTheme();
        
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleTheme);
        }
    });
    
    // Expor funções globalmente
    window.ThemeManager = {
        setTheme,
        toggleTheme,
        getCurrentTheme,
        THEMES
    };
    
})();
