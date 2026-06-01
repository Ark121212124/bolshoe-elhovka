// Адрес backend API системы обращений.
// Локально используется http://localhost:8000.
// На Render при деплое из render.yaml используется сервис:
// https://bolsheelxovskiy-appeals-api.onrender.com
// Если на Render вы назвали backend иначе, замените PRODUCTION_API на фактический адрес backend.
(function () {
  const LOCAL_API = 'http://localhost:8000';
  const PRODUCTION_API = 'https://bolsheelxovskiy-appeals-api.onrender.com';
  const host = window.location.hostname;
  const isLocal = host === 'localhost' || host === '127.0.0.1' || host === '';
  const savedApi = localStorage.getItem('appeals_api_url');

  window.APPEALS_API_URL = window.APPEALS_API_URL || savedApi || (isLocal ? LOCAL_API : PRODUCTION_API);
  window.CRM_PANEL_URL = window.CRM_PANEL_URL || `${window.APPEALS_API_URL.replace(/\/$/, '')}/crm`;
})();
