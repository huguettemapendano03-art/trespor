// Pulse Analytics Main Application Script

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // 1. THEME TOGGLE LOGIC (Dark / Light Mode)
  const themeToggles = document.querySelectorAll('#theme-toggle, #theme-toggle-mobile');

  // Check localStorage or system preference
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.documentElement.classList.remove('dark');
  } else {
    document.documentElement.classList.add('dark');
  }

  themeToggles.forEach(btn => {
    btn.addEventListener('click', () => {
      if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      }
    });
  });

  // 2. MOBILE MENU DRAWER TOGGLE
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });

    // Close mobile menu when clicking a link
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
      });
    });
  }

  // 3. PRICING TOGGLE (Monthly vs Annual)
  const billingMonthlyBtn = document.getElementById('billing-monthly');
  const billingAnnualBtn = document.getElementById('billing-annual');
  const priceAmounts = document.querySelectorAll('.price-amount');

  if (billingMonthlyBtn && billingAnnualBtn) {
    billingMonthlyBtn.addEventListener('click', () => {
      billingMonthlyBtn.className = 'px-5 py-2 rounded-xl text-sm font-bold text-white bg-brand-600 shadow-md transition-all';
      billingAnnualBtn.className = 'px-5 py-2 rounded-xl text-sm font-bold text-slate-400 hover:text-white transition-all flex items-center gap-2';

      priceAmounts.forEach(el => {
        const monthlyVal = el.getAttribute('data-monthly');
        if (monthlyVal) el.textContent = `${monthlyVal} €`;
      });
    });

    billingAnnualBtn.addEventListener('click', () => {
      billingAnnualBtn.className = 'px-5 py-2 rounded-xl text-sm font-bold text-white bg-brand-600 shadow-md transition-all flex items-center gap-2';
      billingMonthlyBtn.className = 'px-5 py-2 rounded-xl text-sm font-bold text-slate-400 hover:text-white transition-all';

      priceAmounts.forEach(el => {
        const annualVal = el.getAttribute('data-annual');
        if (annualVal) el.textContent = `${annualVal} €`;
      });
    });
  }

  // 4. FAQ ACCORDION LOGIC
  const faqTriggers = document.querySelectorAll('.faq-trigger');
  faqTriggers.forEach(btn => {
    btn.addEventListener('click', () => {
      const content = btn.nextElementSibling;
      const icon = btn.querySelector('[data-lucide="chevron-down"]');

      const isOpen = !content.classList.contains('hidden');

      // Close all open FAQs
      document.querySelectorAll('.faq-content').forEach(c => c.classList.add('hidden'));
      document.querySelectorAll('.faq-trigger [data-lucide="chevron-down"]').forEach(i => i.style.transform = 'rotate(0deg)');

      if (!isOpen) {
        content.classList.remove('hidden');
        if (icon) icon.style.transform = 'rotate(180deg)';
      }
    });
  });

  // 5. AUTH TAB SWITCHING (Login vs Register)
  const tabLoginBtn = document.getElementById('tab-login-btn');
  const tabRegisterBtn = document.getElementById('tab-register-btn');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  // Check URL params for tab query (e.g. login.html?tab=register)
  const urlParams = new URLSearchParams(window.location.search);
  const initialTab = urlParams.get('tab');

  function switchToLogin() {
    if (!tabLoginBtn || !tabRegisterBtn) return;
    tabLoginBtn.className = 'flex-1 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 text-white bg-brand-600 shadow-md';
    tabRegisterBtn.className = 'flex-1 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 text-slate-400 hover:text-white';
    if (loginForm) loginForm.classList.remove('hidden');
    if (registerForm) registerForm.classList.add('hidden');
  }

  function switchToRegister() {
    if (!tabLoginBtn || !tabRegisterBtn) return;
    tabRegisterBtn.className = 'flex-1 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 text-white bg-brand-600 shadow-md';
    tabLoginBtn.className = 'flex-1 py-2.5 text-sm font-bold rounded-xl transition-all duration-200 text-slate-400 hover:text-white';
    if (registerForm) registerForm.classList.remove('hidden');
    if (loginForm) loginForm.classList.add('hidden');
  }

  if (tabLoginBtn && tabRegisterBtn) {
    tabLoginBtn.addEventListener('click', switchToLogin);
    tabRegisterBtn.addEventListener('click', switchToRegister);

    if (initialTab === 'register') {
      switchToRegister();
    }
  }

  // 6. PASSWORD VISIBILITY TOGGLE
  const togglePasswordBtns = document.querySelectorAll('.toggle-password-btn');
  togglePasswordBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '<i data-lucide="eye-off" class="w-4 h-4"></i>';
      } else {
        input.type = 'password';
        btn.innerHTML = '<i data-lucide="eye" class="w-4 h-4"></i>';
      }
      if (window.lucide) window.lucide.createIcons();
    });
  });

  // 7. PASSWORD STRENGTH METER
  const regPasswordInput = document.getElementById('reg-password');
  const strengthBar = document.getElementById('strength-bar');
  const strengthLabel = document.getElementById('strength-label');

  if (regPasswordInput && strengthBar && strengthLabel) {
    regPasswordInput.addEventListener('input', (e) => {
      const val = e.target.value;
      let score = 0;

      if (val.length >= 8) score += 25;
      if (/[A-Z]/.test(val)) score += 25;
      if (/[0-9]/.test(val)) score += 25;
      if (/[^A-Za-z0-9]/.test(val)) score += 25;

      strengthBar.style.width = `${Math.max(score, 10)}%`;

      if (score <= 25) {
        strengthBar.className = 'h-full bg-rose-500 transition-all duration-300';
        strengthLabel.textContent = 'Faible';
        strengthLabel.className = 'font-bold text-rose-400';
      } else if (score <= 50) {
        strengthBar.className = 'h-full bg-amber-500 transition-all duration-300';
        strengthLabel.textContent = 'Moyen';
        strengthLabel.className = 'font-bold text-amber-400';
      } else if (score <= 75) {
        strengthBar.className = 'h-full bg-blue-500 transition-all duration-300';
        strengthLabel.textContent = 'Bon';
        strengthLabel.className = 'font-bold text-blue-400';
      } else {
        strengthBar.className = 'h-full bg-emerald-500 transition-all duration-300';
        strengthLabel.textContent = 'Très Fort';
        strengthLabel.className = 'font-bold text-emerald-400';
      }
    });
  }

  // 8. FORM SUBMISSION FEEDBACK & TOAST NOTIFICATION
  function showToast(message, type = 'success') {
    let toast = document.getElementById('global-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'global-toast';
      toast.className = 'fixed bottom-6 right-6 z-50 px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 border text-sm font-semibold toast-animate backdrop-blur-xl';
      document.body.appendChild(toast);
    }

    if (type === 'success') {
      toast.className = 'fixed bottom-6 right-6 z-50 px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 border text-sm font-semibold toast-animate backdrop-blur-xl bg-slate-900/90 border-emerald-500/50 text-emerald-300';
      toast.innerHTML = `<i data-lucide="check-circle-2" class="w-5 h-5 text-emerald-400"></i><span>${message}</span>`;
    } else {
      toast.className = 'fixed bottom-6 right-6 z-50 px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 border text-sm font-semibold toast-animate backdrop-blur-xl bg-slate-900/90 border-amber-500/50 text-amber-300';
      toast.innerHTML = `<i data-lucide="alert-circle" class="w-5 h-5 text-amber-400"></i><span>${message}</span>`;
    }

    if (window.lucide) window.lucide.createIcons();

    setTimeout(() => {
      if (toast) toast.remove();
    }, 4000);
  }

  // Login Submit
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      showToast(`Connexion réussie ! Bienvenue ${email}`, 'success');
      setTimeout(() => {
        window.location.href = 'index.html';
      }, 1500);
    });
  }

  // Register Submit
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('reg-fullname').value;
      showToast(`Compte créé avec succès ! Bienvenue à bord ${name}.`, 'success');
      setTimeout(() => {
        window.location.href = 'index.html';
      }, 1500);
    });
  }

  // Social Auth Click Handler
  const socialBtns = document.querySelectorAll('.social-auth-btn');
  socialBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      showToast("Redirection vers le fournisseur d'authentification...", 'info');
    });
  });

  // Hero Email CTA Form
  const heroCtaForm = document.getElementById('hero-cta-form');
  if (heroCtaForm) {
    heroCtaForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = heroCtaForm.querySelector('input[type="email"]');
      if (emailInput && emailInput.value) {
        showToast(`Merci ! Votre invitation a été envoyée à ${emailInput.value}`, 'success');
        emailInput.value = '';
      }
    });
  }
});
