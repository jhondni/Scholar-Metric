document.addEventListener('DOMContentLoaded', () => {
    const cadastroForm = document.getElementById('cadastroForm');

    if (cadastroForm) {
        cadastroForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Registration attempt detected');

            // Simulação de criação de conta bem-sucedida
            alert('Conta criada com sucesso! Você será redirecionado para o login.');
            window.location.href = 'login.html';
        });
    }
});