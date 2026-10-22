/* PAWSAFE — interações da tela de login. A autenticação real depende do back-end. */
(() => {
  const form = document.getElementById('loginForm');
  if (!form) return;
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  const message = document.getElementById('loginMessage');
  const toggle = document.getElementById('togglePassword');
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  toggle?.addEventListener('click', () => {
    const showing = password.type === 'password';
    password.type = showing ? 'text' : 'password';
    toggle.innerHTML = showing ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
    toggle.setAttribute('aria-label', showing ? 'Ocultar senha' : 'Mostrar senha');
    toggle.setAttribute('aria-pressed', String(showing));
    password.focus();
  });

  document.getElementById('helpLink')?.addEventListener('click', (event) => {
    event.preventDefault();
    message.className = 'alert alert-info login-alert';
    message.textContent = 'Para recuperar o acesso, entre em contato com o administrador do PAWSAFE.';
  });

  [email, password].forEach(field => field.addEventListener('input', () => {
    field.classList.remove('is-invalid');
    message.classList.add('d-none');
  }));

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    message.classList.add('d-none');
    let valid = true;
    if (!email.value.trim() || !email.validity.valid) {
      email.classList.add('is-invalid');
      valid = false;
    }
    if (!password.value.trim()) {
      password.classList.add('is-invalid');
      valid = false;
    }
    if (!valid) {
      message.className = 'alert alert-warning login-alert';
      message.textContent = 'Confira o e-mail e a senha antes de continuar.';
      return;
    }
    // Protótipo visual: não valida credenciais e não realiza autenticação real.
    message.className = 'alert alert-info login-alert';
    message.textContent = 'Tela demonstrativa: a autenticação será conectada ao back-end do PAWSAFE.';
  });
})();
