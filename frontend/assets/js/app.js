const nav = document.querySelector('.nav-links');
const toggle = document.querySelector('.mobile-toggle');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
}
const current = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('[data-link]').forEach(link => {
  const href = link.getAttribute('href');
  if (href === current) link.classList.add('active');
});
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('visible');
    });
  }, {threshold: .14});
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
} else {
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
}
const parallax = document.querySelector('.parallax');
if (parallax) {
  window.addEventListener('mousemove', e => {
    const x = (e.clientX / window.innerWidth - 0.5) * 10;
    const y = (e.clientY / window.innerHeight - 0.5) * 10;
    parallax.style.transform = `translate(${x}px, ${y}px)`;
  });
}

(function () {
  const root = document.documentElement;
  root.setAttribute('data-theme', localStorage.getItem('bolsheelhovskoe_theme') || 'light');
  const nav = document.querySelector('.nav-links');
  if (nav && !document.querySelector('.theme-toggle')) {
    const btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.type = 'button';
    const setLabel = () => { btn.innerHTML = root.getAttribute('data-theme') === 'dark' ? '☀️ Светлая тема' : '🌙 Тёмная тема'; };
    btn.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('bolsheelhovskoe_theme', next);
      setLabel();
    });
    setLabel();
    nav.appendChild(btn);
  }

  const API_BASE = (window.APPEALS_API_URL || localStorage.getItem('appeals_api_url') || 'http://localhost:8000').replace(/\/$/, '');
  const CRM_URL = window.CRM_PANEL_URL || `${API_BASE}/crm`;
  document.querySelectorAll('[data-crm-link]').forEach(a => a.setAttribute('href', CRM_URL));

  const escapeHtml = (v) => String(v || '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');

  async function requestStatus(number, phone) {
    const url = `${API_BASE}/api/appeals/status?number=${encodeURIComponent(number)}&phone=${encodeURIComponent(phone)}`;
    const res = await fetch(url);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Не удалось найти обращение');
    return data;
  }

  async function submitAppeal(data) {
    const fd = new FormData();
    fd.append('citizen_full_name', data.citizen_full_name);
    fd.append('citizen_phone', data.citizen_phone);
    fd.append('citizen_address', data.citizen_address || '');
    fd.append('category_name', data.category_name || 'Другое');
    fd.append('title', data.title);
    fd.append('text', data.text);
    fd.append('consent_personal_data', data.consent_personal_data ? 'true' : 'false');
    if (data.photo) fd.append('photo', data.photo);
    const res = await fetch(`${API_BASE}/api/appeals`, { method: 'POST', body: fd });
    const answer = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(answer.detail || 'Не удалось отправить обращение');
    return answer;
  }

  function renderStatusResult(data) {
    return `<div class="status-result"><h3>Обращение ${escapeHtml(data.number)}</h3><p><b>Тема:</b> ${escapeHtml(data.title)}</p><p><b>Категория:</b> ${escapeHtml(data.category || '—')}</p><p><b>Статус:</b> <span class="appeal-status">${escapeHtml(data.status)}</span></p><p><b>Создано:</b> ${new Date(data.created_at).toLocaleString('ru-RU')}</p><p><b>Обновлено:</b> ${new Date(data.updated_at).toLocaleString('ru-RU')}</p>${(data.comments || []).length ? `<h4>Ответы администрации</h4>${data.comments.map(c => `<p>${escapeHtml(c.comment)}</p>`).join('')}` : ''}</div>`;
  }

  const statusForm = document.getElementById('statusLookupForm');
  if (statusForm) {
    statusForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const result = document.getElementById('statusLookupResult');
      result.innerHTML = '<p>Ищем обращение...</p>';
      try {
        const data = await requestStatus(statusForm.number.value.trim(), statusForm.phone.value.trim());
        result.innerHTML = renderStatusResult(data);
      } catch (e) {
        result.innerHTML = `<p class="form-message error">${escapeHtml(e.message)}</p>`;
      }
    });
  }

  if (!document.querySelector('.chat-widget')) {
    const launcher = document.createElement('button');
    launcher.className = 'chat-launcher'; launcher.type = 'button'; launcher.innerHTML = '💬 Помощник';
    const widget = document.createElement('section');
    widget.className = 'chat-widget'; widget.setAttribute('aria-label', 'Чат-помощник администрации');
    widget.innerHTML = `<div class="chat-head"><div><strong>Помощник поселения</strong><span>Помогу составить обращение и отправить его в CRM-систему администрации.</span></div><button class="chat-close" type="button" aria-label="Закрыть чат">×</button></div><div class="chat-body" id="chatBody"></div><div class="chat-quick"><button type="button" data-chat="appeal">Подать обращение</button><button type="button" data-chat="status">Проверить статус</button><button type="button" data-chat="contacts">Контакты</button><button type="button" data-chat="address">Адрес</button></div><form class="chat-input-row" id="chatForm"><input id="chatInput" autocomplete="off" placeholder="Введите ответ..."><button type="submit">➜</button></form>`;
    document.body.appendChild(widget); document.body.appendChild(launcher);

    const body = widget.querySelector('#chatBody');
    const input = widget.querySelector('#chatInput');
    const form = widget.querySelector('#chatForm');
    let flow = null;

    function msg(text, type='bot') {
      const div = document.createElement('div');
      div.className = `chat-msg ${type}`;
      div.innerHTML = text;
      body.appendChild(div);
      body.scrollTop = body.scrollHeight;
      return div;
    }

    function buttonMsg(buttons) {
      const holder = msg(`<div class="chat-inline-buttons">${buttons.map(b => `<button type="button" data-value="${escapeHtml(b.value)}">${escapeHtml(b.label)}</button>`).join('')}</div>`);
      holder.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => handleUserText(btn.dataset.value, btn.textContent)));
    }

    const appealSteps = [
      {key:'citizen_full_name', question:'Укажите ваше ФИО полностью.'},
      {key:'citizen_phone', question:'Укажите номер телефона для связи.'},
      {key:'citizen_address', question:'Укажите адрес или населенный пункт, к которому относится обращение.'},
      {key:'category_name', question:'Выберите категорию обращения.', buttons:['ЖКХ и благоустройство','Дороги и транспорт','Безопасность','Земельные вопросы','Социальная сфера','Другое']},
      {key:'title', question:'Коротко напишите тему обращения.'},
      {key:'text', question:'Опишите проблему подробнее: что произошло, где, когда и что нужно сделать.'},
      {key:'photo', question:'Прикрепите фотографию, если она есть. Можно пропустить этот шаг.', file:true},
      {key:'consent_personal_data', question:'Подтвердите согласие на обработку персональных данных для регистрации обращения.', buttons:['Согласен','Отмена']},
    ];

    function startAppeal() {
      flow = {type:'appeal', step:0, data:{}};
      msg('<b>Оформление обращения</b><br><span style="color:var(--muted)">Я пошагово соберу данные и отправлю обращение в CRM-систему.</span>');
      askStep();
    }

    function askStep() {
      const step = appealSteps[flow.step];
      msg(step.question);
      if (step.buttons) buttonMsg(step.buttons.map(x => ({label:x, value:x})));
      if (step.file) {
        const holder = msg(`<div class="appeal-form"><input type="file" accept="image/jpeg,image/png,image/webp"><button type="button">Пропустить фото</button></div>`);
        holder.querySelector('input').addEventListener('change', (event) => {
          flow.data.photo = event.target.files[0] || null;
          msg(flow.data.photo ? `Фото выбрано: ${escapeHtml(flow.data.photo.name)}` : 'Фото не выбрано', 'user');
          flow.step += 1; askStep();
        });
        holder.querySelector('button').addEventListener('click', () => { flow.data.photo = null; msg('Пропустить фото', 'user'); flow.step += 1; askStep(); });
      }
    }

    function showConfirm() {
      const d = flow.data;
      msg(`<b>Проверьте обращение:</b><br><b>ФИО:</b> ${escapeHtml(d.citizen_full_name)}<br><b>Телефон:</b> ${escapeHtml(d.citizen_phone)}<br><b>Адрес:</b> ${escapeHtml(d.citizen_address)}<br><b>Категория:</b> ${escapeHtml(d.category_name)}<br><b>Тема:</b> ${escapeHtml(d.title)}<br><b>Фото:</b> ${d.photo ? escapeHtml(d.photo.name) : 'не прикреплено'}<br><br>Отправить обращение в CRM?`);
      buttonMsg([{label:'Отправить', value:'__submit_appeal'}, {label:'Отмена', value:'__cancel'}]);
    }

    async function finishAppeal() {
      msg('Отправляю обращение в CRM-систему...');
      try {
        const answer = await submitAppeal(flow.data);
        msg(`Готово! Обращение зарегистрировано.<br><b>Номер:</b> ${escapeHtml(answer.number)}<br><b>Статус:</b> ${escapeHtml(answer.status)}<br><span style="color:var(--muted)">Сохраните номер: по нему можно проверить статус обращения.</span>`);
      } catch (e) {
        msg(`Не удалось отправить обращение: ${escapeHtml(e.message)}<br><span style="color:var(--muted)">Проверьте, запущен ли backend API по адресу ${escapeHtml(API_BASE)}.</span>`);
      }
      flow = null;
    }

    function startStatus() {
      flow = {type:'status', step:0, data:{}};
      msg('Укажите номер обращения, например BR-2026-00001.');
    }

    async function finishStatus() {
      try {
        msg('Проверяю статус обращения...');
        const data = await requestStatus(flow.data.number, flow.data.phone);
        msg(renderStatusResult(data));
      } catch (e) {
        msg(escapeHtml(e.message));
      }
      flow = null;
    }

    function handleUserText(raw, visible) {
      const text = String(raw || '').trim();
      if (!text) return;
      msg(escapeHtml(visible || text), 'user');
      if (text === '__cancel' || text === 'Отмена') { flow = null; msg('Действие отменено.'); return; }
      if (text === '__submit_appeal') return finishAppeal();

      if (flow?.type === 'appeal') {
        const step = appealSteps[flow.step];
        if (step.key === 'consent_personal_data') {
          if (text !== 'Согласен') { flow = null; msg('Без согласия обращение не отправляется.'); return; }
          flow.data.consent_personal_data = true;
          return showConfirm();
        }
        if (!step.file) {
          flow.data[step.key] = text;
          flow.step += 1;
          if (flow.step < appealSteps.length) askStep(); else showConfirm();
        }
        return;
      }

      if (flow?.type === 'status') {
        if (flow.step === 0) { flow.data.number = text; flow.step = 1; msg('Теперь укажите телефон, который был указан в обращении.'); return; }
        if (flow.step === 1) { flow.data.phone = text; return finishStatus(); }
      }

      answer(classify(text));
    }

    function answer(kind) {
      const data = {
        contacts: '<b>Контакты администрации:</b><br>Тел.: +7 (83441) 3-09-90<br>Тел.: +7 (83441) 3-09-91<br>E-mail: admelh@mail.ru',
        address: '<b>Адрес администрации:</b><br>Республика Мордовия, Лямбирский район, с. Большая Елховка, ул. Фабричная, д. 21.',
        hours: '<b>Личный прием граждан:</b><br>Запись на прием осуществляется по телефону: +7 (83441) 3-09-90.',
        unknown: 'Я могу помочь оформить обращение, проверить его статус, подсказать контакты или адрес администрации.'
      };
      if (kind === 'appeal') return startAppeal();
      if (kind === 'status') return startStatus();
      msg(data[kind] || data.unknown);
    }

    const classify = (text) => {
      const t = text.toLowerCase();
      if (/(статус|провер|номер обращения)/.test(t)) return 'status';
      if (/(контакт|телефон|номер|почт)/.test(t)) return 'contacts';
      if (/(адрес|где|находит|проезд)/.test(t)) return 'address';
      if (/(при[её]м|график|работ|часы)/.test(t)) return 'hours';
      if (/(обращ|жалоб|заяв|написать|сообщить|проблем)/.test(t)) return 'appeal';
      return 'unknown';
    };

    launcher.addEventListener('click', () => widget.classList.toggle('open'));
    widget.querySelector('.chat-close').addEventListener('click', () => widget.classList.remove('open'));
    widget.querySelectorAll('[data-chat]').forEach(btn => btn.addEventListener('click', () => answer(btn.dataset.chat)));
    form.addEventListener('submit', (event) => { event.preventDefault(); const text = input.value.trim(); input.value = ''; handleUserText(text); });
    msg('Здравствуйте! Я помощник сайта. Могу оформить обращение с ФИО, телефоном, адресом, текстом и фотографией, а затем отправить его в CRM-систему администрации.');
  }
})();
