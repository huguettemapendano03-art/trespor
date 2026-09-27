// EduBulletin — Core Application JavaScript

// Initial State and Configuration Presets
const DEFAULT_PRESETS = {
  fr: {
    systemType: 'numeric-20',
    maxGrade: 20,
    passGrade: 10,
    badgeText: 'Système : Francophone /20',
    subjects: [
      { id: 'sub-1', name: 'Mathématiques', coef: 4, teacher: 'M. Dupont' },
      { id: 'sub-2', name: 'Physique-Chimie', coef: 3, teacher: 'Mme Martin' },
      { id: 'sub-3', name: 'SVT (Sciences de la Vie)', coef: 2, teacher: 'M. Leroy' },
      { id: 'sub-4', name: 'Français & Littérature', coef: 3, teacher: 'Mme Bernard' },
      { id: 'sub-5', name: 'Histoire-Géographie', coef: 2, teacher: 'M. Petit' },
      { id: 'sub-6', name: 'Anglais (LV1)', coef: 2, teacher: 'Mme Moreau' },
      { id: 'sub-7', name: 'Philosophie', coef: 2, teacher: 'M. Thomas' }
    ]
  },
  us: {
    systemType: 'alpha-us',
    maxGrade: 4,
    passGrade: 2,
    badgeText: 'Système : Anglophone (GPA 4.0)',
    subjects: [
      { id: 'sub-1', name: 'AP Mathematics / Calculus', coef: 1, teacher: 'Mr. Smith' },
      { id: 'sub-2', name: 'Physics & Chemistry', coef: 1, teacher: 'Ms. Johnson' },
      { id: 'sub-3', name: 'English Literature', coef: 1, teacher: 'Mr. Williams' },
      { id: 'sub-4', name: 'World History', coef: 1, teacher: 'Ms. Brown' },
      { id: 'sub-5', name: 'Spanish Language', coef: 1, teacher: 'Mrs. Davis' }
    ]
  },
  pct: {
    systemType: 'numeric-100',
    maxGrade: 100,
    passGrade: 50,
    badgeText: 'Système : Pourcentage %',
    subjects: [
      { id: 'sub-1', name: 'Mathématiques', coef: 1, teacher: 'M. Kassi' },
      { id: 'sub-2', name: 'Sciences de la Terre', coef: 1, teacher: 'Mme N\'Guessan' },
      { id: 'sub-3', name: 'Langues & Communication', coef: 1, teacher: 'M. Koné' },
      { id: 'sub-4', name: 'Histoire & Citoyenneté', coef: 1, teacher: 'Mme Traoré' }
    ]
  }
};

let appState = {
  schoolName: "Lycée International de L'Avenir",
  schoolSub: "Ministère de l'Éducation Nationale — Paris / Abidjan / Yaoundé",
  className: "Terminales S1",
  schoolYear: "2024 - 2025",
  term: "1er Trimestre",
  headmaster: "Mme Isabelle Dubois",
  systemType: "numeric-20",
  maxGrade: 20,
  passGrade: 10,
  subjects: [...DEFAULT_PRESETS.fr.subjects],
  students: [
    {
      id: 'std-1',
      mat: 'MAT-2024-001',
      name: 'KOUASSI Alexandre',
      gender: 'M',
      dob: '2007-05-14',
      grades: {
        'sub-1': { grade: 17.5, comment: 'Résultats excellents et participation exemplaire.' },
        'sub-2': { grade: 16.0, comment: 'Trés bon niveau théorique et pratique.' },
        'sub-3': { grade: 15.0, comment: 'Travail sérieux et régulier.' },
        'sub-4': { grade: 14.5, comment: 'Bonne qualité de rédaction.' },
        'sub-5': { grade: 16.5, comment: 'Remarquable esprit de synthèse.' },
        'sub-6': { grade: 18.0, comment: 'Aisance orale parfaite.' },
        'sub-7': { grade: 13.0, comment: 'Bon ensemble, continuez ainsi.' }
      }
    },
    {
      id: 'std-2',
      mat: 'MAT-2024-002',
      name: 'DIALLO Aminata',
      gender: 'F',
      dob: '2007-09-22',
      grades: {
        'sub-1': { grade: 18.5, comment: 'Capacités exceptionnelles en résolution de problèmes.' },
        'sub-2': { grade: 17.5, comment: 'Compréhension rapide et rigoureuse.' },
        'sub-3': { grade: 16.5, comment: 'Très bon investissement.' },
        'sub-4': { grade: 15.0, comment: 'Expression écrite très soignée.' },
        'sub-5': { grade: 17.0, comment: 'Excellents résultats.' },
        'sub-6': { grade: 16.0, comment: 'Participation active.' },
        'sub-7': { grade: 14.5, comment: 'Reflexion mûre et approfondie.' }
      }
    },
    {
      id: 'std-3',
      mat: 'MAT-2024-003',
      name: 'BENALI Youssef',
      gender: 'M',
      dob: '2007-01-10',
      grades: {
        'sub-1': { grade: 11.0, comment: 'Ensemble convenable, des efforts à poursuivre.' },
        'sub-2': { grade: 10.5, comment: 'Moyen, la méthode doit être approfondie.' },
        'sub-3': { grade: 12.0, comment: 'Des progrès visibles ce trimestre.' },
        'sub-4': { grade: 13.0, comment: 'Bons résultats à l\'écrit.' },
        'sub-5': { grade: 11.5, comment: 'Passable, révisions régulières indispensables.' },
        'sub-6': { grade: 14.0, comment: 'Bonne participation en classe.' },
        'sub-7': { grade: 10.0, comment: 'Juste la moyenne, il faut intensified le travail.' }
      }
    }
  ],
  selectedSubjectId: 'sub-1',
  selectedStudentId: 'std-1'
};

// LocalStorage Helper
function loadStateFromStorage() {
  const saved = localStorage.getItem('edubulletin_state');
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      appState = { ...appState, ...parsed };
    } catch (e) {
      console.error('Failed to parse state from localStorage', e);
    }
  }
}

function saveStateToStorage() {
  localStorage.setItem('edubulletin_state', JSON.stringify(appState));
}

// Global Toast Notification Helper
function showToast(message, type = 'success') {
  let toast = document.getElementById('global-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'global-toast';
    document.body.appendChild(toast);
  }

  const isSuccess = type === 'success';
  toast.className = `fixed bottom-6 right-6 z-50 px-5 py-3.5 rounded-2xl shadow-2xl flex items-center gap-3 border text-sm font-semibold toast-animate backdrop-blur-xl ${
    isSuccess
      ? 'bg-slate-900/90 border-emerald-500/50 text-emerald-300'
      : 'bg-slate-900/90 border-amber-500/50 text-amber-300'
  }`;

  toast.innerHTML = `<i data-lucide="${isSuccess ? 'check-circle-2' : 'alert-circle'}" class="w-5 h-5 ${isSuccess ? 'text-emerald-400' : 'text-amber-400'}"></i><span>${message}</span>`;

  if (window.lucide) window.lucide.createIcons();

  setTimeout(() => {
    if (toast) toast.remove();
  }, 3500);
}

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
  loadStateFromStorage();

  // Initialize Lucide Icons
  if (window.lucide) window.lucide.createIcons();

  // Theme Toggle Logic
  initThemeToggle();

  // Tab Navigation Logic
  initNavigation();

  // Config Page Logic
  initConfigPage();

  // Students Page Logic
  initStudentsPage();

  // Grades Entry Logic
  initGradesPage();

  // Report Card & PDF Logic
  initReportPage();

  // Initial Sync UI
  syncAllUI();
});

// Theme Switcher
function initThemeToggle() {
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.documentElement.classList.remove('dark');
  } else {
    document.documentElement.classList.add('dark');
  }

  btn.addEventListener('click', () => {
    if (document.documentElement.classList.contains('dark')) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
  });
}

// Navigation Tabs Manager
function initNavigation() {
  const tabs = [
    { navId: 'nav-tab-config', mobileId: 'mobile-nav-config', sectionId: 'tab-section-config' },
    { navId: 'nav-tab-students', mobileId: 'mobile-nav-students', sectionId: 'tab-section-students' },
    { navId: 'nav-tab-grades', mobileId: 'mobile-nav-grades', sectionId: 'tab-section-grades' },
    { navId: 'nav-tab-report', mobileId: 'mobile-nav-report', sectionId: 'tab-section-report' }
  ];

  function switchTab(targetSectionId) {
    tabs.forEach(t => {
      const section = document.getElementById(t.sectionId);
      const navBtn = document.getElementById(t.navId);
      const mobileBtn = document.getElementById(t.mobileId);

      if (t.sectionId === targetSectionId) {
        if (section) section.classList.remove('hidden');
        if (navBtn) {
          navBtn.className = 'nav-tab active px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 bg-brand-600 text-white shadow-md';
        }
        if (mobileBtn) {
          mobileBtn.className = 'mobile-nav-tab active px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap bg-brand-600 text-white';
        }
      } else {
        if (section) section.classList.add('hidden');
        if (navBtn) {
          navBtn.className = 'nav-tab px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 text-slate-400 hover:text-white';
        }
        if (mobileBtn) {
          mobileBtn.className = 'mobile-nav-tab px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap text-slate-400 bg-slate-900';
        }
      }
    });

    if (window.lucide) window.lucide.createIcons();
  }

  tabs.forEach(t => {
    const desktopBtn = document.getElementById(t.navId);
    const mobileBtn = document.getElementById(t.mobileId);

    if (desktopBtn) desktopBtn.addEventListener('click', () => switchTab(t.sectionId));
    if (mobileBtn) mobileBtn.addEventListener('click', () => switchTab(t.sectionId));
  });
}

// Config Page Logic
function initConfigPage() {
  // Preset Buttons
  document.getElementById('preset-fr')?.addEventListener('click', () => applyPreset('fr'));
  document.getElementById('preset-us')?.addEventListener('click', () => applyPreset('us'));
  document.getElementById('preset-pct')?.addEventListener('click', () => applyPreset('pct'));

  // Add Subject Button
  document.getElementById('add-subject-btn')?.addEventListener('click', () => {
    const newId = 'sub-' + Date.now();
    appState.subjects.push({
      id: newId,
      name: 'Nouvelle Matière',
      coef: 1,
      teacher: 'M. Prof'
    });
    renderSubjectsList();
    saveStateToStorage();
    showToast('Matière ajoutée', 'success');
  });

  // Save Configuration Button
  document.getElementById('save-config-btn')?.addEventListener('click', () => {
    appState.schoolName = document.getElementById('config-school-name').value;
    appState.schoolSub = document.getElementById('config-school-sub').value;
    appState.className = document.getElementById('config-class-name').value;
    appState.schoolYear = document.getElementById('config-school-year').value;
    appState.term = document.getElementById('config-term').value;
    appState.headmaster = document.getElementById('config-headmaster').value;
    appState.systemType = document.getElementById('config-system-type').value;
    appState.maxGrade = parseFloat(document.getElementById('config-max-grade').value) || 20;
    appState.passGrade = parseFloat(document.getElementById('config-pass-grade').value) || 10;

    saveStateToStorage();
    syncAllUI();
    showToast('Configuration enregistrée avec succès !', 'success');

    // Automatically navigate to Students Tab
    document.getElementById('nav-tab-students')?.click();
  });
}

function applyPreset(presetKey) {
  const preset = DEFAULT_PRESETS[presetKey];
  if (!preset) return;

  appState.systemType = preset.systemType;
  appState.maxGrade = preset.maxGrade;
  appState.passGrade = preset.passGrade;
  appState.subjects = JSON.parse(JSON.stringify(preset.subjects));

  document.getElementById('config-system-type').value = preset.systemType;
  document.getElementById('config-max-grade').value = preset.maxGrade;
  document.getElementById('config-pass-grade').value = preset.passGrade;

  document.getElementById('active-system-badge').textContent = preset.badgeText;

  renderSubjectsList();
  saveStateToStorage();
  showToast(`Modèle ${presetKey.toUpperCase()} appliqué`, 'success');
}

function renderSubjectsList() {
  const container = document.getElementById('subjects-list-container');
  if (!container) return;

  container.innerHTML = '';
  let totalCoef = 0;

  appState.subjects.forEach((sub, index) => {
    totalCoef += parseFloat(sub.coef) || 0;

    const div = document.createElement('div');
    div.className = 'flex items-center gap-2 p-2 rounded-xl bg-slate-950 border border-slate-800 text-xs';
    div.innerHTML = `
      <input type="text" value="${sub.name}" data-id="${sub.id}" data-field="name" class="subject-input flex-grow bg-transparent text-slate-100 font-semibold focus:outline-none border-b border-transparent focus:border-brand-500 px-1">
      <div class="flex items-center gap-1">
        <span class="text-slate-500 font-bold">Coef:</span>
        <input type="number" value="${sub.coef}" min="1" max="10" data-id="${sub.id}" data-field="coef" class="subject-input w-12 bg-slate-900 text-center rounded border border-slate-700 font-bold text-brand-400 py-0.5">
      </div>
      <button data-id="${sub.id}" class="remove-subject-btn p-1 text-slate-500 hover:text-rose-400 transition-colors" title="Supprimer">
        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
      </button>
    `;
    container.appendChild(div);
  });

  document.getElementById('total-coefficients-display').textContent = totalCoef;
  document.getElementById('total-subjects-display').textContent = appState.subjects.length;

  if (window.lucide) window.lucide.createIcons();

  // Attach Input listeners
  container.querySelectorAll('.subject-input').forEach(input => {
    input.addEventListener('change', (e) => {
      const id = e.target.getAttribute('data-id');
      const field = e.target.getAttribute('data-field');
      const sub = appState.subjects.find(s => s.id === id);
      if (sub) {
        sub[field] = field === 'coef' ? (parseFloat(e.target.value) || 1) : e.target.value;
        saveStateToStorage();
        renderSubjectsList();
      }
    });
  });

  // Attach Delete listeners
  container.querySelectorAll('.remove-subject-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = btn.getAttribute('data-id');
      if (appState.subjects.length <= 1) {
        showToast('Vous devez garder au moins une matière.', 'warning');
        return;
      }
      appState.subjects = appState.subjects.filter(s => s.id !== id);
      renderSubjectsList();
      saveStateToStorage();
      showToast('Matière supprimée', 'success');
    });
  });
}

// Calculations & Stats Logic
function calculateStudentAverage(student) {
  let totalWeightedPoints = 0;
  let totalCoef = 0;

  appState.subjects.forEach(sub => {
    const gradeObj = student.grades[sub.id];
    if (gradeObj && gradeObj.grade !== undefined && gradeObj.grade !== '') {
      const val = parseFloat(gradeObj.grade);
      if (!isNaN(val)) {
        totalWeightedPoints += val * (sub.coef || 1);
        totalCoef += (sub.coef || 1);
      }
    }
  });

  if (totalCoef === 0) return { average: 0, totalPoints: 0, totalCoef: 0 };
  const avg = totalWeightedPoints / totalCoef;
  return {
    average: Math.round(avg * 100) / 100,
    totalPoints: Math.round(totalWeightedPoints * 100) / 100,
    totalCoef
  };
}

function calculateClassRanks() {
  const studentAvgs = appState.students.map(s => {
    const calc = calculateStudentAverage(s);
    return { id: s.id, average: calc.average };
  });

  studentAvgs.sort((a, b) => b.average - a.average);

  const ranks = {};
  studentAvgs.forEach((item, index) => {
    ranks[item.id] = index + 1;
  });

  return ranks;
}

function calculateSubjectClassStats(subjectId) {
  const grades = [];
  appState.students.forEach(s => {
    const gObj = s.grades[subjectId];
    if (gObj && gObj.grade !== undefined && gObj.grade !== '') {
      const v = parseFloat(gObj.grade);
      if (!isNaN(v)) grades.push(v);
    }
  });

  if (grades.length === 0) return { min: 0, max: 0, avg: 0 };

  const min = Math.min(...grades);
  const max = Math.max(...grades);
  const sum = grades.reduce((acc, curr) => acc + curr, 0);
  const avg = Math.round((sum / grades.length) * 100) / 100;

  return { min, max, avg };
}

// Students Page Logic
function initStudentsPage() {
  const modal = document.getElementById('add-student-modal');
  const addBtn = document.getElementById('add-student-btn');
  const closeBtn = document.getElementById('close-modal-btn');
  const cancelBtn = document.getElementById('cancel-modal-btn');
  const form = document.getElementById('add-student-form');
  const demoBtn = document.getElementById('demo-students-btn');

  if (addBtn && modal) {
    addBtn.addEventListener('click', () => modal.classList.remove('hidden'));
  }
  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  }
  if (cancelBtn && modal) {
    cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));
  }

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('modal-student-name').value;
      const mat = document.getElementById('modal-student-mat').value || ('MAT-' + Date.now().toString().slice(-4));
      const gender = document.getElementById('modal-student-gender').value;
      const dob = document.getElementById('modal-student-dob').value || '2007-01-01';

      const newStudent = {
        id: 'std-' + Date.now(),
        mat,
        name,
        gender,
        dob,
        grades: {}
      };

      appState.students.push(newStudent);
      saveStateToStorage();
      syncAllUI();

      if (modal) modal.classList.add('hidden');
      form.reset();
      showToast(`Élève ${name} ajouté avec succès`, 'success');
    });
  }

  if (demoBtn) {
    demoBtn.addEventListener('click', () => {
      appState.students = [
        ...DEFAULT_PRESETS.fr.subjects ? appState.students : []
      ];
      saveStateToStorage();
      syncAllUI();
      showToast('Exemple de classe rechargé', 'success');
    });
  }
}

function renderStudentsTable() {
  const tbody = document.getElementById('students-table-body');
  if (!tbody) return;

  tbody.innerHTML = '';
  const ranks = calculateClassRanks();

  appState.students.forEach((s) => {
    const calc = calculateStudentAverage(s);
    const rank = ranks[s.id] || '-';

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-900/50 transition-colors';
    tr.innerHTML = `
      <td class="px-6 py-4 font-mono text-xs text-slate-400">${s.mat}</td>
      <td class="px-6 py-4 font-bold text-white flex items-center gap-2">
        <div class="w-7 h-7 rounded-full bg-brand-500/10 text-brand-400 flex items-center justify-center text-xs font-bold">
          ${s.name.charAt(0)}
        </div>
        <span>${s.name}</span>
      </td>
      <td class="px-6 py-4 text-xs">${s.gender === 'M' ? 'Masculin' : 'Féminin'}</td>
      <td class="px-6 py-4 text-xs text-slate-400">${s.dob}</td>
      <td class="px-6 py-4 text-center font-extrabold text-brand-400 text-base">${calc.average} / ${appState.maxGrade}</td>
      <td class="px-6 py-4 text-center">
        <span class="px-2.5 py-1 rounded-lg text-xs font-bold ${rank === 1 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-slate-800 text-slate-300'}">
          ${rank}${rank === 1 ? 'er' : 'ème'}
        </span>
      </td>
      <td class="px-6 py-4 text-right">
        <button data-id="${s.id}" class="delete-student-btn p-2 text-slate-500 hover:text-rose-400 transition-colors" title="Supprimer">
          <i data-lucide="trash-2" class="w-4 h-4"></i>
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  if (window.lucide) window.lucide.createIcons();

  tbody.querySelectorAll('.delete-student-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      appState.students = appState.students.filter(s => s.id !== id);
      saveStateToStorage();
      syncAllUI();
      showToast('Élève supprimé', 'success');
    });
  });
}

// Grades Entry Logic
function initGradesPage() {
  const subjectSelect = document.getElementById('grade-entry-subject-select');
  const autoCommentBtn = document.getElementById('auto-fill-comments-btn');

  if (subjectSelect) {
    subjectSelect.addEventListener('change', (e) => {
      appState.selectedSubjectId = e.target.value;
      renderGradesEntryTable();
    });
  }

  if (autoCommentBtn) {
    autoCommentBtn.addEventListener('click', () => {
      const selectedSubId = appState.selectedSubjectId;
      const sub = appState.subjects.find(s => s.id === selectedSubId);
      if (!sub) return;

      appState.students.forEach(s => {
        if (!s.grades[selectedSubId]) s.grades[selectedSubId] = { grade: 0, comment: '' };
        const val = parseFloat(s.grades[selectedSubId].grade) || 0;

        let comment = '';
        if (val >= 16) comment = 'Excellent travail, très grande maîtrise et rigueur.';
        else if (val >= 14) comment = 'Très bon trimestre, travail sérieux et régulier.';
        else if (val >= 12) comment = 'Bon travail d\'ensemble, poursuivez vos efforts.';
        else if (val >= 10) comment = 'Ensemble juste convenable, soyez plus attentif.';
        else comment = 'Résultats insuffisants, révisions et travail soutenus requis.';

        s.grades[selectedSubId].comment = comment;
      });

      saveStateToStorage();
      renderGradesEntryTable();
      showToast('Appréciations générées automatiquement', 'success');
    });
  }
}

function renderGradesEntryTable() {
  const subjectSelect = document.getElementById('grade-entry-subject-select');
  const tbody = document.getElementById('grades-entry-table-body');
  const badge = document.getElementById('selected-subject-badge');

  if (!tbody || !subjectSelect) return;

  // Populate subject options
  subjectSelect.innerHTML = appState.subjects.map(s =>
    `<option value="${s.id}" ${s.id === appState.selectedSubjectId ? 'selected' : ''}>${s.name} (Coef ${s.coef})</option>`
  ).join('');

  const currentSub = appState.subjects.find(s => s.id === appState.selectedSubjectId) || appState.subjects[0];
  if (!currentSub) return;

  if (badge) badge.textContent = `${currentSub.name} (Coef ${currentSub.coef})`;

  tbody.innerHTML = '';

  appState.students.forEach((s, idx) => {
    const gradeObj = s.grades[currentSub.id] || { grade: '', comment: '' };

    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-900/50 transition-colors';
    tr.innerHTML = `
      <td class="px-6 py-4 text-xs font-bold text-slate-500">${idx + 1}</td>
      <td class="px-6 py-4 font-bold text-white">${s.name}</td>
      <td class="px-6 py-4">
        <input type="number" step="0.5" min="0" max="${appState.maxGrade}" value="${gradeObj.grade !== undefined ? gradeObj.grade : ''}"
          data-student-id="${s.id}" class="grade-input w-24 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-brand-400 font-extrabold text-sm focus:border-brand-500">
      </td>
      <td class="px-6 py-4">
        <input type="text" value="${gradeObj.comment || ''}" placeholder="Appréciation du professeur..."
          data-student-id="${s.id}" class="comment-input w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:border-brand-500">
      </td>
      <td class="px-6 py-4 text-center">
        <span class="px-2 py-1 rounded text-[10px] font-bold ${gradeObj.grade >= appState.passGrade ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}">
          ${gradeObj.grade >= appState.passGrade ? 'Saisi' : 'À améliorer'}
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Input events
  tbody.querySelectorAll('.grade-input').forEach(inp => {
    inp.addEventListener('change', (e) => {
      const studentId = e.target.getAttribute('data-student-id');
      const student = appState.students.find(s => s.id === studentId);
      if (student) {
        if (!student.grades[currentSub.id]) student.grades[currentSub.id] = {};
        student.grades[currentSub.id].grade = e.target.value !== '' ? parseFloat(e.target.value) : '';
        saveStateToStorage();
        renderStudentsTable();
      }
    });
  });

  tbody.querySelectorAll('.comment-input').forEach(inp => {
    inp.addEventListener('change', (e) => {
      const studentId = e.target.getAttribute('data-student-id');
      const student = appState.students.find(s => s.id === studentId);
      if (student) {
        if (!student.grades[currentSub.id]) student.grades[currentSub.id] = {};
        student.grades[currentSub.id].comment = e.target.value;
        saveStateToStorage();
      }
    });
  });
}

// Report Page & PDF Export Logic
function initReportPage() {
  const studentSelect = document.getElementById('report-student-select');
  const downloadPdfBtn = document.getElementById('download-pdf-btn');
  const printBtn = document.getElementById('print-bulletin-btn');

  if (studentSelect) {
    studentSelect.addEventListener('change', (e) => {
      appState.selectedStudentId = e.target.value;
      renderReportCardPreview();
    });
  }

  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }

  if (downloadPdfBtn) {
    downloadPdfBtn.addEventListener('click', () => {
      const element = document.getElementById('bulletin-pdf-wrapper');
      const currentStudent = appState.students.find(s => s.id === appState.selectedStudentId) || appState.students[0];
      const filename = `Bulletin_${currentStudent ? currentStudent.name.replace(/\s+/g, '_') : 'Eleve'}_${appState.term.replace(/\s+/g, '_')}.pdf`;

      showToast('Génération du PDF en cours...', 'info');

      if (window.html2pdf) {
        const opt = {
          margin:       0.3,
          filename:     filename,
          image:        { type: 'jpeg', quality: 0.98 },
          html2canvas:  { scale: 2, useCORS: true },
          jsPDF:        { unit: 'in', format: 'a4', orientation: 'portrait' }
        };

        window.html2pdf().set(opt).from(element).save().then(() => {
          showToast('Téléchargement du PDF terminé !', 'success');
        }).catch(err => {
          console.error(err);
          showToast('Erreur lors du téléchargement PDF', 'warning');
        });
      } else {
        window.print();
      }
    });
  }
}

function renderReportCardPreview() {
  const studentSelect = document.getElementById('report-student-select');
  if (!studentSelect) return;

  // Populate student dropdown
  studentSelect.innerHTML = appState.students.map(s =>
    `<option value="${s.id}" ${s.id === appState.selectedStudentId ? 'selected' : ''}>${s.name} (${s.mat})</option>`
  ).join('');

  const student = appState.students.find(s => s.id === appState.selectedStudentId) || appState.students[0];
  if (!student) return;

  const ranks = calculateClassRanks();
  const studentCalc = calculateStudentAverage(student);
  const classRanks = ranks[student.id] || 1;

  // Header and Metadata
  document.getElementById('pdf-school-name').textContent = appState.schoolName;
  document.getElementById('pdf-school-sub').textContent = appState.schoolSub;
  document.getElementById('pdf-term-display').textContent = appState.term;
  document.getElementById('pdf-headmaster-display').textContent = appState.headmaster;

  document.getElementById('pdf-student-name').textContent = student.name;
  document.getElementById('pdf-student-mat').textContent = student.mat;
  document.getElementById('pdf-student-gender').textContent = student.gender === 'M' ? 'Masculin' : 'Féminin';
  document.getElementById('pdf-student-dob').textContent = student.dob;

  document.getElementById('pdf-class-name').textContent = appState.className;
  document.getElementById('pdf-class-count').textContent = `${appState.students.length} Élèves`;
  document.getElementById('pdf-system-type').textContent = `Note sur /${appState.maxGrade}`;

  // Grades Table Body
  const tbody = document.getElementById('pdf-grades-tbody');
  tbody.innerHTML = '';

  appState.subjects.forEach(sub => {
    const gObj = student.grades[sub.id] || { grade: '-', comment: '-' };
    const stats = calculateSubjectClassStats(sub.id);

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="p-2.5 border border-slate-300">
        <strong class="text-slate-900 block">${sub.name}</strong>
        <span class="text-[10px] text-slate-500">${sub.teacher || 'Enseignant'}</span>
      </td>
      <td class="p-2.5 border border-slate-300 text-center font-bold">${sub.coef}</td>
      <td class="p-2.5 border border-slate-300 text-center font-black text-brand-700 text-sm">
        ${gObj.grade !== undefined && gObj.grade !== '' ? gObj.grade : '-'}
      </td>
      <td class="p-2.5 border border-slate-300 text-center text-[11px] text-slate-600">
        <strong>${stats.avg}</strong> <br>
        <span class="text-[9px] text-slate-400">(${stats.min} - ${stats.max})</span>
      </td>
      <td class="p-2.5 border border-slate-300 text-slate-700 italic">
        ${gObj.comment || 'Aucune observation.'}
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Footer Totals
  document.getElementById('pdf-total-coef').textContent = studentCalc.totalCoef;
  document.getElementById('pdf-total-points').textContent = `${studentCalc.totalPoints} pts`;

  document.getElementById('pdf-student-moye').textContent = `${studentCalc.average} / ${appState.maxGrade}`;
  document.getElementById('pdf-student-rank').textContent = `${classRanks}${classRanks === 1 ? 'er' : 'ème'} / ${appState.students.length}`;

  // Calculate Overall Class Average
  const allAvgs = appState.students.map(s => calculateStudentAverage(s).average);
  const classAvgSum = allAvgs.reduce((a, b) => a + b, 0);
  const overallClassAvg = allAvgs.length ? Math.round((classAvgSum / allAvgs.length) * 100) / 100 : 0;
  document.getElementById('pdf-class-avg-display').textContent = `Moyenne de classe : ${overallClassAvg} / ${appState.maxGrade}`;

  // Honors & Status
  const statusEl = document.getElementById('pdf-student-status');
  const honorsEl = document.getElementById('pdf-honors-display');

  if (studentCalc.average >= appState.passGrade) {
    statusEl.textContent = 'Admis(e)';
    statusEl.className = 'inline-block px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-100 text-emerald-800';
  } else {
    statusEl.textContent = 'Ajourné(e)';
    statusEl.className = 'inline-block px-2 py-0.5 text-[10px] font-bold rounded bg-rose-100 text-rose-800';
  }

  if (studentCalc.average >= 16) honorsEl.textContent = 'Félicitations du Conseil de Classe';
  else if (studentCalc.average >= 14) honorsEl.textContent = 'Encouragements du Conseil';
  else if (studentCalc.average >= 12) honorsEl.textContent = 'Tableau d\'Honneur';
  else honorsEl.textContent = 'Aucune distinction';
}

// Master UI Sync
function syncAllUI() {
  document.getElementById('config-school-name').value = appState.schoolName;
  document.getElementById('config-school-sub').value = appState.schoolSub;
  document.getElementById('config-class-name').value = appState.className;
  document.getElementById('config-school-year').value = appState.schoolYear;
  document.getElementById('config-term').value = appState.term;
  document.getElementById('config-headmaster').value = appState.headmaster;
  document.getElementById('config-system-type').value = appState.systemType;
  document.getElementById('config-max-grade').value = appState.maxGrade;
  document.getElementById('config-pass-grade').value = appState.passGrade;

  renderSubjectsList();
  renderStudentsTable();
  renderGradesEntryTable();
  renderReportCardPreview();
}
