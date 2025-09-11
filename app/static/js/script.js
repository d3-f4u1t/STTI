
document.addEventListener('DOMContentLoaded', () => {
    const statusEl = document.getElementById('class-status');

    // Simulated example logic (can be replaced with real API calls)
    const now = new Date();
    const classStartTime = new Date();
    classStartTime.setHours(10, 0, 0);

    if (now > classStartTime) {
        statusEl.textContent = 'Started';
        statusEl.className = 'badge bg-success';
    } else {
        statusEl.textContent = 'On Time';
        statusEl.className = 'badge bg-info';
    }
});
