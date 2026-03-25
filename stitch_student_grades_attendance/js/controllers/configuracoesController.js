document.addEventListener('DOMContentLoaded', () => {
    console.log('Configuracoes Controller Initialized');
    
    // Suporte para troca de abas ou salvamento de formulários (simulação)
    const saveButton = document.querySelector('button.bg-primary');
    if (saveButton) {
        saveButton.addEventListener('click', () => {
            alert('Configurações salvas com sucesso!');
        });
    }
});
