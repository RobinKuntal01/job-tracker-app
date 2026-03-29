// ⚠️ API Base URL
const API_BASE = "http://localhost:8000/api/v1";

let apps = [];
let editingId = null;
let editContacts = [];
let refreshInterval = null;
let isGuest = false;
let authToken = null;

// Initialize theme
initTheme();

/* ---- AUTH FUNCTIONS ---- */
function showScreen(which) {
  document.getElementById('loading-screen').style.display = 'none';
  document.getElementById('auth-screen').style.display = which === 'auth' ? 'flex' : 'none';
  document.getElementById('app-screen').style.display = which === 'app' ? 'flex' : 'none';
}

function showLogin() {
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('register-form').style.display = 'none';
}

function showRegister() {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('register-form').style.display = 'block';
}

window.handleAuthKey = (e) => { if(e.key === 'Enter') login(); };
window.handleRegKey = (e) => { if(e.key === 'Enter') register(); };

window.login = async () => {
  const userid = document.getElementById('userid-input').value.trim();
  const password = document.getElementById('password-input').value.trim();
  if(!userid || !password) {
    showAuthError('Please enter both userid and password');
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userid, password })
    });
    
    if(response.ok) {
      const data = await response.json();
      authToken = data.access_token;
      localStorage.setItem('jt_token', authToken);
      localStorage.setItem('jt_userid', userid);
      isGuest = false;
      showScreen('app');
      subscribeToData();
    } else {
      const error = await response.json();
      showAuthError(error.detail || 'Login failed');
    }
  } catch(e) {
    showAuthError('Network error: ' + e.message);
  }
};

window.register = async () => {
  const userid = document.getElementById('reg-userid').value.trim();
  const password = document.getElementById('reg-password').value.trim();
  if(!userid || !password) {
    showAuthError('Please enter both userid and password');
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userid, password })
    });
    
    if(response.ok) {
      showAuthError('Account created! Please login.', 'success');
      showLogin();
    } else {
      const error = await response.json();
      showAuthError(error.detail || 'Registration failed');
    }
  } catch(e) {
    showAuthError('Network error: ' + e.message);
  }
};

window.continueAsGuest = () => {
  isGuest = true;
  authToken = null;
  localStorage.removeItem('jt_token');
  localStorage.removeItem('jt_userid');
  // Load guest data from localStorage
  const guestData = localStorage.getItem('jt_guest_data');
  if(guestData) {
    apps = JSON.parse(guestData);
  } else {
    apps = [];
  }
  showScreen('app');
  renderAll();
};

window.signOut = () => {
  if(!isGuest && refreshInterval) {
    clearInterval(refreshInterval);
  }
  authToken = null;
  isGuest = false;
  apps = [];
  localStorage.removeItem('jt_token');
  localStorage.removeItem('jt_userid');
  showScreen('auth');
  showLogin();
};

function showAuthError(msg, type = 'error') {
  const el = document.getElementById('auth-error');
  el.textContent = msg;
  el.style.color = type === 'success' ? 'var(--green)' : 'var(--red)';
}

// Auto-login if token exists
const savedToken = localStorage.getItem('jt_token');
if(savedToken) {
  authToken = savedToken;
  isGuest = false;
  showScreen('app');
  subscribeToData();
} else {
  showScreen('auth');
  showLogin();
}

/* ---- API FUNCTIONS ---- */
async function subscribeToData() {
  if(isGuest) return; // No polling for guest
  
  await refreshData();
  // Refresh data every 5 seconds
  if (refreshInterval) clearInterval(refreshInterval);
  refreshInterval = setInterval(refreshData, 5000);
}

async function refreshData() {
  if(isGuest) return;
  
  try {
    const user_id = localStorage.getItem('jt_userid');
    const response = await fetch(`${API_BASE}/jobs/${user_id}`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    apps = await response.json();
    renderAll();
  } catch (e) {
    showToast('Sync error: ' + e.message, 'err');
  }
}

window._saveApp = async (obj) => {
  if(isGuest) {
    // For guest, save to localStorage
    if(obj._id) {
      // Update existing
      const index = apps.findIndex(a => a._id === obj._id);
      if(index !== -1) {
        apps[index] = { ...apps[index], ...obj };
      }
    } else {
      // Create new
      obj._id = Date.now().toString();
      obj.created_at = new Date().toISOString();
      obj.updated_at = new Date().toISOString();
      obj.user_id = 'guest';
      apps.push(obj);
    }
    localStorage.setItem('jt_guest_data', JSON.stringify(apps));
    renderAll();
    return { message: "Saved locally" };
  }
  
  setSyncing(true);
  try {
    let url = `${API_BASE}/jobs`;
    let method = 'POST';
    obj.user_id = localStorage.getItem('jt_userid') || 'unknown';
    let body = obj;
    if (obj._id) {
      // Update existing
      url = `${API_BASE}/jobs/${obj._id}`;
      method = 'PUT';
      const { _id, ...updateData } = obj;
      body = updateData;
    }

    const response = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    await refreshData();
  } catch (e) {
    showToast('Save failed: ' + e.message, 'err');
  }
  setSyncing(false);
};

window._deleteApp = async (id) => {
  if(isGuest) {
    // For guest, remove from localStorage
    apps = apps.filter(a => a._id !== id);
    localStorage.setItem('jt_guest_data', JSON.stringify(apps));
    renderAll();
    return { message: "Deleted locally" };
  }
  
  setSyncing(true);
  try {
    const response = await fetch(`${API_BASE}/jobs/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    await refreshData();
  } catch (e) {
    showToast('Delete failed: ' + e.message, 'err');
  }
  setSyncing(false);
};


function renderAll() { renderStats(); renderTable(); }

function renderStats() {
  let total=apps.length, applied=0, interview=0, offer=0, rejected=0;
  apps.forEach(a => {
    if(['applied','screening'].includes(a.status)) applied++;
    if(['interview','technical'].includes(a.status)) interview++;
    if(a.status==='offer') offer++;
    if(['rejected','ghosted'].includes(a.status)) rejected++;
  });
  document.getElementById('st-total').textContent = total;
  document.getElementById('st-applied').textContent = applied;
  document.getElementById('st-interview').textContent = interview;
  document.getElementById('st-offer').textContent = offer;
  document.getElementById('st-rejected').textContent = rejected;
}

window.filterByStatus = (s) => {
  document.getElementById('filter-status').value = s;
  document.querySelectorAll('.stat-pill').forEach(p => p.classList.remove('active'));
  const map = {'':'s-total','applied':'s-applied','interview':'s-interview','offer':'s-offer','rejected':'s-rejected'};
  document.querySelector('.'+(map[s]||'s-total'))?.classList.add('active');
  renderTable();
};

function renderTable() {
  const q = document.getElementById('search-input').value.toLowerCase();
  const fs = document.getElementById('filter-status').value;
  const fp = document.getElementById('filter-platform').value;
  const sort = document.getElementById('sort-by').value;

  let data = apps.filter(a => {
    const mq = !q || [a.company,a.role,a.platform].some(x=>(x||'').toLowerCase().includes(q));
    const ms = !fs || a.status===fs || (fs==='applied'&&a.status==='screening') || (fs==='interview'&&a.status==='technical') || (fs==='rejected'&&a.status==='ghosted');
    const mp = !fp || a.platform===fp;
    return mq && ms && mp;
  });

  if(sort==='date-asc') data.sort((a,b)=>new Date(a.date||0)-new Date(b.date||0));
  else if(sort==='company') data.sort((a,b)=>(a.company||'').localeCompare(b.company||''));
  else if(sort==='status') data.sort((a,b)=>(a.status||'').localeCompare(b.status||''));
  else data.sort((a,b)=>new Date(b.date||0)-new Date(a.date||0));

  const tbody = document.getElementById('table-body');
  const empty = document.getElementById('empty-state');
  if(!data.length) { tbody.innerHTML=''; empty.style.display='block'; return; }
  empty.style.display='none';

  tbody.innerHTML = data.map(a => {
    const ini = (a.company||'??').slice(0,2).toUpperCase();
    const contacts = (a.contacts||[]).map(c => {
      const dot = c.status==='connected'?'🟢':c.status==='requested'?'🟡':'⚪';
      return `<span class="contact-chip">${dot} ${esc(c.name)}${c.department?` <span class="dept">· ${esc(c.department)}</span>`:''}</span>`;
    }).join('');
    const urlBtn = a.url ? `<a href="${esc(a.url)}" target="_blank" onclick="event.stopPropagation()" class="icon-btn" title="Open job URL" style="text-decoration:none">🔗</a>` : '';
    return `<tr onclick="openModal('${a._id}')">
      <td><div class="company-cell">
        <div class="company-logo">${ini}</div>
        <div><div class="company-name">${esc(a.company)}</div><div class="company-role">${esc(a.role)}</div></div>
      </div></td>
      <td><span class="platform-tag">${esc(a.platform||'—')}</span></td>
      <td><span class="badge b-${a.status}">${statusLabel(a.status)}</span></td>
      <td class="date-cell">${fmtDate(a.date)}</td>
      <td>${contacts||'<span style="color:var(--text3);font-size:11px">None</span>'}</td>
      <td style="max-width:160px;color:var(--text2);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(a.notes||'')}</td>
      <td><div class="row-actions">${urlBtn}
        <button class="icon-btn" onclick="openModal('${a._id}');event.stopPropagation()" title="Edit">✏️</button>
        <button class="icon-btn del" onclick="deleteApp(event,'${a._id}')" title="Delete">🗑</button>
      </div></td>
    </tr>`;
  }).join('');
}

/* ---- MODAL ---- */
window.openModal = (id) => {
  editingId = id || null;
  editContacts = [];
  const a = id ? apps.find(x=>x._id===id) : null;
  document.getElementById('modal-title').textContent = a ? 'Edit Application' : 'New Application';
  document.getElementById('f-company').value = a?.company||'';
  document.getElementById('f-role').value = a?.role||'';
  document.getElementById('f-platform').value = a?.platform||'LinkedIn';
  document.getElementById('f-status').value = a?.status||'applied';
  document.getElementById('f-date').value = a?.date||new Date().toISOString().split('T')[0];
  document.getElementById('f-url').value = a?.url||'';
  document.getElementById('f-notes').value = a?.notes||'';
  editContacts = a?.contacts ? JSON.parse(JSON.stringify(a.contacts)) : [];
  // Map database department field to form dept field for editing
  editContacts = editContacts.map(c => ({
    name: c.name,
    dept: c.department || '',
    role: c.role || '',
    status: c.status || 'not_sent'
  }));
  renderContacts();
  document.getElementById('modal-overlay').classList.add('open');
  setTimeout(()=>document.getElementById('f-company').focus(), 50);
};

window.closeModal = () => { document.getElementById('modal-overlay').classList.remove('open'); editingId=null; editContacts=[]; };
window.closeOnBackdrop = (e) => { if(e.target===document.getElementById('modal-overlay')) closeModal(); };

function renderContacts() {
  const list = document.getElementById('contacts-list');
  list.innerHTML = editContacts.map((c,i)=>{
    const cls = c.status==='connected'?'c-connected':c.status==='requested'?'c-requested':'c-not-sent';
    const lbl = c.status==='connected'?'Connected':c.status==='requested'?'Requested':'Not Sent';
    return `<div class="contact-card">
      <div><div class="cn">${esc(c.name)}</div><div class="cd">${esc(c.dept||'')}${c.dept&&c.role?' · ':''}${esc(c.role||'')}</div></div>
      <span class="conn-badge ${cls}">${lbl}</span>
      <button class="icon-btn del" onclick="removeContact(${i})" style="opacity:1">✕</button>
    </div>`;
  }).join('');
}

window.addContact = () => {
  const name = document.getElementById('nc-name').value.trim();
  const dept = document.getElementById('nc-dept').value.trim();
  const status = document.getElementById('nc-status').value;
  if(!name) { showToast('Enter a contact name', 'err'); return; }
  editContacts.push({name, dept, status});
  renderContacts();
  document.getElementById('nc-name').value='';
  document.getElementById('nc-dept').value='';
  document.getElementById('nc-status').value='requested';
  document.getElementById('nc-name').focus();
};

window.removeContact = (i) => { editContacts.splice(i,1); renderContacts(); };

window.saveApp = async () => {
  const company = document.getElementById('f-company').value.trim();
  const role = document.getElementById('f-role').value.trim();
  if(!company||!role) { showToast('Company and role are required', 'err'); return; }
  const btn = document.getElementById('save-btn');
  btn.textContent = 'Saving...'; btn.disabled = true;
  
  // Transform contacts: map dept to department
  const contacts = editContacts.map(c => ({
    name: c.name,
    department: c.dept || '',
    role: c.role || '',
    status: c.status || 'not_sent'
  }));

  const obj = {
    company,
    role,
    platform: document.getElementById('f-platform').value,
    status: document.getElementById('f-status').value,
    date: document.getElementById('f-date').value,
    url: document.getElementById('f-url').value.trim(),
    notes: document.getElementById('f-notes').value.trim(),
    contacts: contacts
  };
  
  // If editing, include the _id
  if (editingId) {
    obj._id = editingId;
  }
  
  await window._saveApp(obj);
  btn.textContent = 'Save'; btn.disabled = false;
  closeModal();
  showToast(editingId ? 'Application updated ✓' : 'Application added ✓', 'ok');
};

window.deleteApp = async (e, id) => {
  e.stopPropagation();
  if(!confirm('Delete this application?')) return;
  await window._deleteApp(id);
  showToast('Deleted', '');
};

/* ---- HELPERS ---- */
function esc(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmtDate(d) {
  if(!d) return '—';
  const dt = new Date(d+'T00:00:00');
  return dt.toLocaleDateString('en-IN',{day:'numeric',month:'short',year:'2-digit'});
}
function statusLabel(s) {
  return {applied:'Applied',screening:'Screening',interview:'Interview',technical:'Technical',offer:'Offer',rejected:'Rejected',ghosted:'Ghosted'}[s]||s;
}
function setSyncing(v) {
  const dot = document.getElementById('sync-dot');
  const lbl = document.getElementById('sync-label');
  dot.className = 'sync-dot' + (v?' syncing':'');
  lbl.textContent = v ? 'Syncing...' : 'Live';
}
function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent=msg; t.className='toast '+(type||'');
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'), 2500);
}

/* ---- THEME TOGGLE ---- */
function initTheme() {
  const saved = localStorage.getItem('jt_theme') || 'dark';
  if (saved === 'light') {
    document.body.classList.add('light');
  }
  updateThemeButton(saved);
}

window.toggleTheme = () => {
  const isLight = document.body.classList.contains('light');
  if (isLight) {
    document.body.classList.remove('light');
    localStorage.setItem('jt_theme', 'dark');
    updateThemeButton('dark');
  } else {
    document.body.classList.add('light');
    localStorage.setItem('jt_theme', 'light');
    updateThemeButton('light');
  }
};

function updateThemeButton(theme) {
  const btn = document.getElementById('theme-toggle');
  btn.textContent = theme === 'dark' ? '🌙' : '☀️';
}

// Initialize theme on load
initTheme();