// main.js — UI interactions: notification sidebar, remove items, animate svg paths

document.addEventListener('DOMContentLoaded', function() {

  // Offcanvas elements (Bootstrap 5)
  const notifBtn = document.getElementById('notifBtn');
  const notifOffcanvasEl = document.getElementById('notifOffcanvas');
  let notifOffcanvas = null;
  if (notifOffcanvasEl) notifOffcanvas = new bootstrap.Offcanvas(notifOffcanvasEl);

  // Simple store for demo notifications (in future, fetch from server)
  const notifications = [
    { id: 1, text: "New assignment available in Cybersecurity.", type: "info" },
    { id: 2, text: "Class canceled tomorrow (Maths).", type: "warn" },
    { id: 3, text: "New message from Admin.", type: "msg" }
  ];

  const notifList = document.getElementById('notificationsContainer');
  const notifCount = document.getElementById('notifCount');

  function renderNotifications() {
    if (!notifList) return;
    notifList.innerHTML = '';
    if (notifications.length === 0) {
      notifList.innerHTML = '<div class="text-muted small">No notifications</div>';
      notifCount.textContent = '0';
      return;
    }
    notifications.forEach(n => {
      const el = document.createElement('div');
      el.className = 'list-group-item d-flex justify-content-between align-items-start';
      el.dataset.id = n.id;
      el.innerHTML = `
        <div class="ms-2 me-auto">
          <div class="fw-semibold">${n.type === 'warn' ? '⚠️' : n.type === 'msg' ? '📩' : '📢'} ${n.text}</div>
          <small class="text-muted">Just now</small>
        </div>
        <button class="btn btn-sm btn-link removeNotif">✖</button>
      `;
      notifList.appendChild(el);
    });
    notifCount.textContent = String(notifications.length);
  }

  // remove single notification
  document.addEventListener('click', function(e) {
    if (e.target && e.target.classList.contains('removeNotif')) {
      const item = e.target.closest('[data-id]');
      const id = Number(item.dataset.id);
      const idx = notifications.findIndex(n => n.id === id);
      if (idx > -1) notifications.splice(idx, 1);
      renderNotifications();
    }
  });

  // clear all
  const clearAll = document.getElementById('clearAll');
  if (clearAll) {
    clearAll.addEventListener('click', function() {
      notifications.splice(0, notifications.length);
      renderNotifications();
    });
  }

  // open offcanvas on click
  if (notifBtn && notifOffcanvas) {
    notifBtn.addEventListener('click', function() {
      notifOffcanvas.show();
    });
  }

  const closeNotif = document.getElementById('closeNotif')
  if (closeNotif) closeNotif.addEventListener('click', () => notifOffcanvas.hide());

  // initial render
  renderNotifications();

  // tiny SVG path animation re-trigger on resize (keeps it lively)
  const paths = document.querySelectorAll('#svgLines path');
  function animatePaths() {
    paths.forEach(p => {
      p.style.strokeDasharray = p.getTotalLength();
      p.style.strokeDashoffset = p.getTotalLength();
      p.getBoundingClientRect(); // force reflow
      p.style.transition = 'stroke-dashoffset 1.2s ease';
      p.style.strokeDashoffset = '0';
    });
  }
  animatePaths();
  window.addEventListener('resize', () => setTimeout(animatePaths, 200));
});
