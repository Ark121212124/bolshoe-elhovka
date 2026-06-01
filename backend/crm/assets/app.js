const state = {
  apiBase: localStorage.getItem('crm_api_base') || location.origin,
  token: localStorage.getItem('crm_token') || '',
  user: JSON.parse(localStorage.getItem('crm_user') || 'null'),
  statuses: [],
  users: [],
  appeals: [],
  selectedId: null,
};

const $ = (id) => document.getElementById(id);
const fmt = (value) => value ? new Date(value).toLocaleString('ru-RU') : '—';
const esc = (v) => String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');
const api = (path, options = {}) => fetch(`${state.apiBase}${path}`, {
  ...options,
  headers: {
    ...(options.headers || {}),
    ...(state.token ? {Authorization: `Bearer ${state.token}`} : {}),
  },
});

function statusClass(status){
  if(status === 'Новое') return 'status-new';
  if(['В работе','Назначено','Принято'].includes(status)) return 'status-work';
  if(['Выполнено','Закрыто'].includes(status)) return 'status-done';
  if(['Отклонено','Требуется уточнение'].includes(status)) return 'status-danger';
  return '';
}

function showApp(logged){
  $('loginView').hidden = logged;
  $('crmView').hidden = !logged;
  $('logoutBtn').hidden = !logged;
  if(logged){
    $('currentUser').textContent = `${state.user.full_name} · роль: ${state.user.role}`;
  }
}

async function login(){
  state.apiBase = $('apiBase').value.trim().replace(/\/$/, '') || location.origin;
  $('loginError').textContent = '';
  const res = await fetch(`${state.apiBase}/api/auth/login`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({username:$('username').value.trim(), password:$('password').value})
  });
  if(!res.ok){
    const data = await res.json().catch(()=>({detail:'Ошибка входа'}));
    $('loginError').textContent = data.detail || 'Ошибка входа';
    return;
  }
  const data = await res.json();
  state.token = data.access_token;
  state.user = data.user;
  localStorage.setItem('crm_api_base', state.apiBase);
  localStorage.setItem('crm_token', state.token);
  localStorage.setItem('crm_user', JSON.stringify(state.user));
  showApp(true);
  await initData();
}

function logout(){
  state.token = '';
  state.user = null;
  localStorage.removeItem('crm_token');
  localStorage.removeItem('crm_user');
  showApp(false);
}

async function initData(){
  await Promise.all([loadStatuses(), loadUsers(), loadStats(), loadAppeals()]);
}

async function loadStatuses(){
  const res = await api('/api/crm/statuses');
  if(!res.ok) return;
  state.statuses = await res.json();
  $('statusFilter').innerHTML = '<option value="">Все статусы</option>' + state.statuses.map(s => `<option>${esc(s)}</option>`).join('');
}

async function loadUsers(){
  const res = await api('/api/crm/users');
  if(!res.ok) return;
  state.users = await res.json();
}

async function loadStats(){
  const res = await api('/api/crm/stats');
  if(!res.ok) return;
  const data = await res.json();
  const parts = [`<div class="stat"><strong>${data.total}</strong><span>Всего обращений</span></div>`];
  Object.entries(data.by_status || {}).forEach(([k,v]) => parts.push(`<div class="stat"><strong>${v}</strong><span>${esc(k)}</span></div>`));
  $('stats').innerHTML = parts.join('');
}

async function loadAppeals(){
  const params = new URLSearchParams();
  if($('statusFilter').value) params.set('status', $('statusFilter').value);
  if($('searchInput').value.trim()) params.set('q', $('searchInput').value.trim());
  const res = await api(`/api/crm/appeals?${params}`);
  if(!res.ok){ logout(); return; }
  state.appeals = await res.json();
  renderAppeals();
}

function renderAppeals(){
  const holder = $('appealsList');
  if(!state.appeals.length){ holder.innerHTML = '<p class="empty-detail">Обращений пока нет.</p>'; return; }
  holder.innerHTML = state.appeals.map(item => `
    <article class="appeal-card ${item.id === state.selectedId ? 'active' : ''}" data-id="${item.id}">
      <div class="meta"><span class="badge ${statusClass(item.status)}">${esc(item.status)}</span><span class="badge">${esc(item.number)}</span></div>
      <b>${esc(item.title)}</b>
      <p>${esc(item.citizen_full_name)} · ${esc(item.citizen_phone)}</p>
      <div class="meta"><span class="badge">${esc(item.category || 'Без категории')}</span><span class="badge">фото: ${item.file_count}</span></div>
    </article>
  `).join('');
  holder.querySelectorAll('[data-id]').forEach(card => card.addEventListener('click', () => selectAppeal(Number(card.dataset.id))));
}

async function selectAppeal(id){
  state.selectedId = id;
  renderAppeals();
  const res = await api(`/api/crm/appeals/${id}`);
  if(!res.ok) return;
  const item = await res.json();
  renderDetail(item);
}

function renderDetail(item){
  const userOptions = '<option value="">Не назначен</option>' + state.users.map(u => `<option value="${u.id}" ${u.full_name === item.assigned_to ? 'selected' : ''}>${esc(u.full_name)} (${esc(u.role)})</option>`).join('');
  const statusOptions = state.statuses.map(s => `<option ${s === item.status ? 'selected' : ''}>${esc(s)}</option>`).join('');
  $('appealDetail').innerHTML = `
    <div class="detail-title">
      <div><h2>${esc(item.title)}</h2><p>${esc(item.number)} · создано ${fmt(item.created_at)}</p></div>
      <span class="badge ${statusClass(item.status)}">${esc(item.status)}</span>
    </div>
    <div class="detail-grid">
      <div class="field"><small>Заявитель</small><b>${esc(item.citizen_full_name)}</b></div>
      <div class="field"><small>Телефон</small><b>${esc(item.citizen_phone)}</b></div>
      <div class="field"><small>Адрес</small><b>${esc(item.citizen_address || 'Не указан')}</b></div>
      <div class="field"><small>Категория</small><b>${esc(item.category || 'Без категории')}</b></div>
    </div>
    <div class="detail-section"><h3>Текст обращения</h3><p>${esc(item.text).replaceAll('\n','<br>')}</p></div>
    <div class="detail-section"><h3>Фотографии</h3>${renderFiles(item.files)}</div>
    <div class="detail-section"><h3>Управление</h3>
      <div class="actions">
        <div class="action-row"><select id="detailStatus">${statusOptions}</select><button class="primary" id="saveStatus">Сменить статус</button></div>
        <div class="action-row"><select id="detailUser">${userOptions}</select><button class="ghost" id="saveAssign">Назначить</button></div>
      </div>
    </div>
    <div class="detail-section"><h3>Комментарии</h3>
      <div>${item.comments.map(c => `<div class="comment"><small>${esc(c.author || 'Система')} · ${fmt(c.created_at)} · ${c.is_public ? 'виден заявителю' : 'служебный'}</small>${esc(c.comment)}</div>`).join('') || '<p>Комментариев пока нет.</p>'}</div>
      <textarea id="commentText" placeholder="Добавить комментарий"></textarea>
      <label class="check"><input id="commentPublic" type="checkbox"> Видно заявителю при проверке статуса</label>
      <button class="primary" id="saveComment">Добавить комментарий</button>
    </div>
    <div class="detail-section"><h3>История</h3><div class="history">${item.history.map(h => `<div class="history-row">${fmt(h.created_at)} — ${esc(h.action)} ${h.old_value ? `: ${esc(h.old_value)} → ${esc(h.new_value)}` : ''}</div>`).join('')}</div></div>
  `;
  $('saveStatus').addEventListener('click', () => updateStatus(item.id));
  $('saveAssign').addEventListener('click', () => assignUser(item.id));
  $('saveComment').addEventListener('click', () => addComment(item.id));
}

function renderFiles(files){
  if(!files || !files.length) return '<p>Фотографии не прикреплены.</p>';
  return `<div class="files">${files.map(f => `<div class="file-card"><img src="${state.apiBase}${f.url}" alt="${esc(f.file_name)}"><a href="${state.apiBase}${f.url}" target="_blank">Открыть фото</a></div>`).join('')}</div>`;
}

async function updateStatus(id){
  await api(`/api/crm/appeals/${id}/status`, {method:'PATCH', headers:{'Content-Type':'application/json'}, body:JSON.stringify({status:$('detailStatus').value})});
  await Promise.all([loadStats(), loadAppeals(), selectAppeal(id)]);
}
async function assignUser(id){
  const v = $('detailUser').value;
  await api(`/api/crm/appeals/${id}/assign`, {method:'PATCH', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:v ? Number(v) : null})});
  await Promise.all([loadStats(), loadAppeals(), selectAppeal(id)]);
}
async function addComment(id){
  const text = $('commentText').value.trim();
  if(!text) return;
  await api(`/api/crm/appeals/${id}/comments`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({comment:text, is_public:$('commentPublic').checked})});
  await selectAppeal(id);
}

$('loginBtn').addEventListener('click', login);
$('logoutBtn').addEventListener('click', logout);
$('refreshBtn').addEventListener('click', () => Promise.all([loadStats(), loadAppeals()]));
$('statusFilter').addEventListener('change', loadAppeals);
$('searchInput').addEventListener('input', () => { clearTimeout(window.searchTimer); window.searchTimer = setTimeout(loadAppeals, 350); });
$('apiBase').value = state.apiBase;

if(state.token && state.user){ showApp(true); initData().catch(logout); } else { showApp(false); }
