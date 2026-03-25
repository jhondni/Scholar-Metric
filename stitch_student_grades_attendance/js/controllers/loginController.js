document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Login attempt detected via Controller');
            // Simulação de autenticação bem-sucedida
            window.location.href = 'painel.html';
        });
    }
});
