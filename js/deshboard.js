/* PAWSAFE Dashboard
   Os números e registros desta demonstração são estáticos.
   Na integração com o back-end, substitua-os por dados recebidos do sistema. */

   document.addEventListener('DOMContentLoaded', () => {
    const dateElement = document.getElementById('currentDate');
    const yearElement = document.getElementById('currentYear');
  
    const now = new Date();
    if (dateElement) {
      dateElement.textContent = new Intl.DateTimeFormat('pt-BR', {
        weekday: 'long', day: '2-digit', month: 'long', year: 'numeric'
      }).format(now);
    }
    if (yearElement) yearElement.textContent = now.getFullYear();
  
    // Menu lateral responsivo
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    const menuToggle = document.getElementById('menuToggle');
  
    const closeMenu = () => {
      sidebar?.classList.remove('is-open');
      backdrop?.classList.remove('is-visible');
      menuToggle?.setAttribute('aria-expanded', 'false');
    };
    const openMenu = () => {
      sidebar?.classList.add('is-open');
      backdrop?.classList.add('is-visible');
      menuToggle?.setAttribute('aria-expanded', 'true');
    };
  
    menuToggle?.addEventListener('click', () => {
      sidebar?.classList.contains('is-open') ? closeMenu() : openMenu();
    });
    backdrop?.addEventListener('click', closeMenu);
    sidebar?.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
      link.addEventListener('click', () => {
        sidebar.querySelectorAll('.nav-link').forEach(item => item.classList.remove('active'));
        link.classList.add('active');
        if (window.innerWidth <= 900) closeMenu();
      });
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) closeMenu();
    });
  
    // Demonstração de ação de sair. Conecte ao fluxo real de autenticação posteriormente.
    document.getElementById('logoutButton')?.addEventListener('click', () => {
      const shouldLeave = window.confirm('Deseja sair do PAWSAFE?');
      if (shouldLeave) {
        window.alert('Este botão é demonstrativo. Conecte-o à rota de logout do back-end.');
      }
    });
  
    // Gráficos Chart.js
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js não foi carregado. Verifique sua conexão com a internet.');
      return;
    }
  
    Chart.defaults.font.family = "'DM Sans', sans-serif";
    Chart.defaults.color = '#718077';
  
    const gridColor = 'rgba(44, 77, 62, 0.08)';
    const adoptionCanvas = document.getElementById('adoptionsChart');
    if (adoptionCanvas) {
      new Chart(adoptionCanvas, {
        type: 'bar',
        data: {
          labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
          datasets: [{
            label: 'Adoções',
            data: [3, 5, 4, 7, 6, 2],
            backgroundColor: '#397665',
            hoverBackgroundColor: '#244438',
            borderRadius: 6,
            borderSkipped: false,
            maxBarThickness: 31
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#19372e',
              padding: 11,
              displayColors: false,
              callbacks: { label: context => ` ${context.parsed.y} adoção(ões)` }
            }
          },
          scales: {
            x: { grid: { display: false }, border: { display: false }, ticks: { padding: 8 } },
            y: {
              beginAtZero: true,
              suggestedMax: 8,
              ticks: { stepSize: 2, padding: 10 },
              grid: { color: gridColor, drawTicks: false },
              border: { display: false }
            }
          }
        }
      });
    }
  
    const speciesCanvas = document.getElementById('speciesChart');
    if (speciesCanvas) {
      new Chart(speciesCanvas, {
        type: 'doughnut',
        data: {
          labels: ['Cães', 'Gatos', 'Outros'],
          datasets: [{
            data: [4, 3, 1],
            backgroundColor: ['#397665', '#78977c', '#c47755'],
            hoverBackgroundColor: ['#244438', '#5f8065', '#a85f40'],
            borderColor: '#ffffff',
            borderWidth: 4,
            hoverOffset: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '72%',
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#19372e',
              padding: 11,
              callbacks: { label: context => ` ${context.label}: ${context.parsed}` }
            }
          }
        }
      });
    }
  });
  