/* PAWSAFE — navegação lateral compartilhada por todas as páginas. */
(() => {
  const mount = document.getElementById('sidebarMount');
  if (!mount) return;

  const inPages = /\/Pages\//i.test(window.location.pathname);
  const pagePrefix = inPages ? '' : 'Pages/';
  const dashboardHref = inPages ? '../index.html' : 'index.html';
  const pageName = (window.location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const activeModule = pageName === 'index.html' ? 'dashboard' : pageName.replace('.html', '').toLowerCase();

  const items = [
    { id: 'dashboard', label: 'Dashboard', icon: 'bi-grid-1x2-fill', href: dashboardHref },
    { id: 'animais', label: 'Animais', icon: 'bi-paw', href: `${pagePrefix}animais.html`, count: true },
    { id: 'adocoes', label: 'Adoções', icon: 'bi-heart', href: `${pagePrefix}adocoes.html` },
    { id: 'resgates', label: 'Resgates', icon: 'bi-house-heart', href: `${pagePrefix}resgates.html` },
    { id: 'voluntarios', label: 'Voluntários & Equipe', icon: 'bi-people', href: `${pagePrefix}voluntarios.html` },
    { id: 'doacoes', label: 'Doações / Financeiro', icon: 'bi-hand-heart', href: `${pagePrefix}doacoes.html` },
    { id: 'estoque', label: 'Estoque', icon: 'bi-box-seam', href: `${pagePrefix}estoque.html` },
    { id: 'relatorios', label: 'Relatório técnico', icon: 'bi-file-earmark-bar-graph', href: `${pagePrefix}relatorios.html` }
  ];

  const navLinks = items.map(item => {
    const active = activeModule === item.id || (item.id === 'dashboard' && activeModule === 'pg_login');
    const count = item.count ? '<span class="sidebar-count" id="navCount">8</span>' : '';
    const chevron = active && item.id === 'dashboard' ? '<i class="bi bi-chevron-right nav-chevron"></i>' : '';
    return `<a class="nav-link${active ? ' active' : ''}" data-module="${item.id}" href="${item.href}"${active ? ' aria-current="page"' : ''}><i class="bi ${item.icon}"></i><span>${item.label}</span>${count}${chevron}</a>`;
  }).join('');

  mount.innerHTML = `
    <aside class="sidebar" id="sidebar" aria-label="Menu principal">
      <a class="brand" href="${dashboardHref}" aria-label="PAWSAFE página inicial">
        <span class="brand-mark"><i class="bi bi-heart-pulse-fill"></i></span>
        <span class="brand-copy"><strong>PAWSAFE</strong><small>Gestão e proteção animal</small></span>
      </a>
      <div class="sidebar-label">MENU PRINCIPAL</div>
      <nav class="nav flex-column sidebar-nav">${navLinks}</nav>
      <div class="sidebar-bottom">
        <a class="nav-link volunteer-link" href="${pagePrefix}voluntarios.html"><i class="bi bi-box-arrow-up-right"></i><span>Link de voluntariado</span></a>
        <button class="nav-link logout-link" type="button" id="logoutButton"><i class="bi bi-box-arrow-left"></i><span>Sair</span></button>
        <div class="profile-mini"><div class="avatar"><i class="bi bi-person-fill"></i></div><div class="profile-text"><strong>Renata Oliveira</strong><small>Administradora</small></div><button class="profile-more" type="button" aria-label="Opções do perfil"><i class="bi bi-three-dots-vertical"></i></button></div>
      </div>
    </aside>
    <div class="sidebar-backdrop" id="sidebarBackdrop"></div>`;

  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  const toggle = document.getElementById('menuToggle');
  const closeMenu = () => {
    sidebar?.classList.remove('is-open', 'open');
    backdrop?.classList.remove('is-visible');
    toggle?.setAttribute('aria-expanded', 'false');
  };
  const openMenu = () => {
    sidebar?.classList.add('is-open', 'open');
    backdrop?.classList.add('is-visible');
    toggle?.setAttribute('aria-expanded', 'true');
  };
  toggle?.addEventListener('click', () => sidebar?.classList.contains('is-open') ? closeMenu() : openMenu());
  backdrop?.addEventListener('click', closeMenu);
  sidebar?.querySelectorAll('.nav-link').forEach(link => link.addEventListener('click', () => {
    if (window.innerWidth <= 900) closeMenu();
  }));
  window.addEventListener('resize', () => { if (window.innerWidth > 900) closeMenu(); });
})();
