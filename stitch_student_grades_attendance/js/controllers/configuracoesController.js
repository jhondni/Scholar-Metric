document.addEventListener('DOMContentLoaded', () => {
    console.log('Configuracoes Controller Initialized');

    // Suporte para troca de abas ou salvamento de formulários (simulação)
    const saveButton = document.querySelector('button.bg-primary');
    if (saveButton) {
        saveButton.addEventListener('click', () => {
            alert('Configurações salvas com sucesso!');
        });
    }

    // Lógica de Alternância de Tema (Modo Escuro)
    const btnClaro = document.getElementById('btn-tema-claro');
    const btnEscuro = document.getElementById('btn-tema-escuro');
    const htmlElement = document.documentElement;

    const updateThemeUI = (theme) => {
        if (theme === 'dark') {
            htmlElement.classList.add('dark');
            htmlElement.classList.remove('light');
            // Atualiza bordas dos botões para feedback visual
            btnEscuro?.classList.add('border-secondary');
            btnEscuro?.classList.remove('border-transparent');
            btnClaro?.classList.remove('border-secondary');
            btnClaro?.classList.add('border-transparent');
        } else {
            htmlElement.classList.remove('dark');
            htmlElement.classList.add('light');
            // Atualiza bordas dos botões para feedback visual
            btnClaro?.classList.add('border-secondary');
            btnClaro?.classList.remove('border-transparent');
            btnEscuro?.classList.remove('border-secondary');
            btnEscuro?.classList.add('border-transparent');
        }
        localStorage.setItem('theme', theme);
    };

    btnClaro?.addEventListener('click', () => updateThemeUI('light'));
    btnEscuro?.addEventListener('click', () => updateThemeUI('dark'));

    // Verifica preferência salva ao carregar a página de configurações
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        updateThemeUI(savedTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        updateThemeUI('dark');
    }
});
