// STTI – main.js

// Live clock
function updateClock() {
    const el = document.getElementById('currentTime');
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

// Sidebar toggle (desktop)
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const content = document.getElementById('content');

if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        if (sidebar.classList.contains('collapsed')) {
            sidebar.style.width = '70px';
            if (content) content.style.marginLeft = '70px';
        } else {
            sidebar.style.width = '250px';
            if (content) content.style.marginLeft = '250px';
        }
    });
}

// Mobile sidebar toggle
const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
if (mobileSidebarToggle && sidebar) {
    mobileSidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && !mobileSidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// Notification badge updater
function updateNotifBadge() {
    fetch('/notifications/unread_count')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('notifBadge');
            if (!badge) return;
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(() => {});
}

// Only poll if authenticated (sidebar exists)
if (document.getElementById('sidebar')) {
    updateNotifBadge();
    setInterval(updateNotifBadge, 30000);
}

// Auto-dismiss flash messages
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
    });
}, 5000);
