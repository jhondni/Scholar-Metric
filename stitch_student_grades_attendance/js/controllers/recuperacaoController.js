document.addEventListener('DOMContentLoaded', () => {
    const recuperacaoForm = document.getElementById('recuperacaoForm');

    if (recuperacaoForm) {
        recuperacaoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            console.log(`Password recovery requested for: ${email}`);

            alert('Se o e-mail informado estiver em nossa base, você receberá um link para redefinir sua senha em instantes.');
            window.location.href = 'login.html';
        });
    }
});