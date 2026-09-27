// static/bulletin.js
let currentStudentId = 1;
let currentBulletinData = null;

document.addEventListener('DOMContentLoaded', () => {
  loadStudent(currentStudentId);
});

function loadStudent(studentId) {
  currentStudentId = studentId;

  // Highlight active student button
  document.querySelectorAll('.student-select-btn').forEach(btn => {
    btn.classList.remove('border-indigo-500', 'bg-indigo-950/40');
  });
  const activeBtn = document.getElementById(`student-btn-${studentId}`);
  if (activeBtn) {
    activeBtn.classList.add('border-indigo-500', 'bg-indigo-950/40');
  }

  fetch(`/api/student/${studentId}/bulletin`)
    .then(res => res.json())
    .then(data => {
      currentBulletinData = data;
      renderStudentHeader(data.student);
      renderEditorTable(data.grades, data.total_obtained, data.total_max, data.percentage);
      renderVisualBulletin(data.student, data.grades, data.total_obtained, data.total_max, data.percentage);
    })
    .catch(err => console.error('Erreur chargement bulletin:', err));
}

function renderStudentHeader(student) {
  document.getElementById('student-name-display').textContent = student.full_name;
  document.getElementById('student-details-display').textContent = `Code: ${student.student_code} | Classe: ${student.classroom} | Année: ${student.school_year}`;
  document.getElementById('btn-download-pdf').href = `/student/${student.id}/download-pdf`;

  document.getElementById('visual-student-name').textContent = student.full_name;
  document.getElementById('visual-student-code').textContent = student.student_code;
  document.getElementById('visual-student-class').textContent = student.classroom;
  document.getElementById('visual-student-year').textContent = student.school_year;
}

function renderEditorTable(grades, totalObtained, totalMax, percentage) {
  const tbody = document.getElementById('grades-table-body');
  tbody.innerHTML = '';

  grades.forEach(g => {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-slate-950/30 transition-colors';

    tr.innerHTML = `
      <td class="p-3 font-bold text-slate-200">${g.subject_name}</td>
      <td class="p-2 text-center"><input type="number" step="0.5" max="10" min="0" value="${g.p1}" onchange="updateGrade(${g.subject_id}, 'p1', this.value)" class="w-16 p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center font-mono text-xs focus:border-indigo-500 focus:outline-none"></td>
      <td class="p-2 text-center"><input type="number" step="0.5" max="10" min="0" value="${g.p2}" onchange="updateGrade(${g.subject_id}, 'p2', this.value)" class="w-16 p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center font-mono text-xs focus:border-indigo-500 focus:outline-none"></td>
      <td class="p-2 text-center"><input type="number" step="0.5" max="20" min="0" value="${g.exam1}" onchange="updateGrade(${g.subject_id}, 'exam1', this.value)" class="w-16 p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center font-mono text-xs focus:border-indigo-500 focus:outline-none"></td>
      <td class="p-3 text-center font-bold text-indigo-400 bg-slate-950/60 font-mono">${g.tot_s1.toFixed(1)}</td>
      <td class="p-2 text-center"><input type="number" step="0.5" max="10" min="0" value="${g.p3}" onchange="updateGrade(${g.subject_id}, 'p3', this.value)" class="w-16 p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center font-mono text-xs focus:border-indigo-500 focus:outline-none"></td>
      <td class="p-2 text-center"><input type="number" step="0.5" max="10" min="0" value="${g.p4}" onchange="updateGrade(${g.subject_id}, 'p4', this.value)" class="w-16 p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center font-mono text-xs focus:border-indigo-500 focus:outline-none"></td>
      <td class="p-2 text-center"><input type="number" step="0.5" max="20" min="0" value="${g.exam2}" onchange="updateGrade(${g.subject_id}, 'exam2', this.value)" class="w-16 p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-center font-mono text-xs focus:border-indigo-500 focus:outline-none"></td>
      <td class="p-3 text-center font-bold text-indigo-400 bg-slate-950/60 font-mono">${g.tot_s2.toFixed(1)}</td>
      <td class="p-3 text-center font-extrabold text-indigo-300 bg-indigo-950/20 font-mono">${g.tot_an.toFixed(1)}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('editor-total-score').textContent = `${totalObtained.toFixed(1)} / ${totalMax}`;
  document.getElementById('editor-percentage').textContent = `${percentage.toFixed(2)} %`;
}

function renderVisualBulletin(student, grades, totalObtained, totalMax, percentage) {
  const tbody = document.getElementById('visual-bulletin-tbody');
  tbody.innerHTML = '';

  grades.forEach(g => {
    const tr = document.createElement('tr');
    tr.className = 'border-b border-slate-900 font-bold';

    tr.innerHTML = `
      <td class="border border-slate-900 p-2 text-left font-extrabold">${g.subject_name}</td>
      <td class="border border-slate-900 p-1 font-mono">${g.p1.toFixed(1)}</td>
      <td class="border border-slate-900 p-1 font-mono">${g.p2.toFixed(1)}</td>
      <td class="border border-slate-900 p-1 font-mono">${g.exam1.toFixed(1)}</td>
      <td class="border border-slate-900 p-1 bg-slate-200 font-extrabold font-mono">${g.tot_s1.toFixed(1)}</td>
      <td class="border border-slate-900 p-1 font-mono">${g.p3.toFixed(1)}</td>
      <td class="border border-slate-900 p-1 font-mono">${g.p4.toFixed(1)}</td>
      <td class="border border-slate-900 p-1 font-mono">${g.exam2.toFixed(1)}</td>
      <td class="border border-slate-900 p-1 bg-slate-200 font-extrabold font-mono">${g.tot_s2.toFixed(1)}</td>
      <td class="border border-slate-900 p-2 bg-indigo-50 font-extrabold text-indigo-900 font-mono text-sm">${g.tot_an.toFixed(1)}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('visual-total-score').textContent = `${totalObtained.toFixed(1)} / ${totalMax}`;
  document.getElementById('visual-percentage').textContent = `${percentage.toFixed(2)} %`;
}

function updateGrade(subjectId, field, value) {
  fetch('/api/grade/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id: currentStudentId,
      subject_id: subjectId,
      field: field,
      value: value
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      loadStudent(currentStudentId);
    }
  })
  .catch(err => console.error('Erreur mise a jour cote:', err));
}

function switchTab(tab) {
  const btnEditor = document.getElementById('btn-tab-editor');
  const btnVisual = document.getElementById('btn-tab-visual');
  const tabEditor = document.getElementById('tab-editor-content');
  const tabVisual = document.getElementById('tab-visual-content');

  if (tab === 'editor') {
    btnEditor.className = 'px-4 py-2 rounded-lg text-xs font-bold text-white bg-indigo-600 shadow transition-all';
    btnVisual.className = 'px-4 py-2 rounded-lg text-xs font-bold text-slate-400 hover:text-white transition-all';
    tabEditor.classList.remove('hidden');
    tabVisual.classList.add('hidden');
  } else {
    btnVisual.className = 'px-4 py-2 rounded-lg text-xs font-bold text-white bg-indigo-600 shadow transition-all';
    btnEditor.className = 'px-4 py-2 rounded-lg text-xs font-bold text-slate-400 hover:text-white transition-all';
    tabVisual.classList.remove('hidden');
    tabEditor.classList.add('hidden');
  }
}
