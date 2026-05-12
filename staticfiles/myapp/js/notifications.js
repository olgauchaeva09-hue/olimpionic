document.addEventListener('DOMContentLoaded', function() {
    const notificationBtn = document.getElementById('notification-btn');
    if (!notificationBtn) return;
    
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationList = document.getElementById('notification-list');
    const notificationBadge = document.getElementById('notification-badge');
    
    if (!notificationDropdown || !notificationList || !notificationBadge) return;
    
    let isOpen = false;
    
    async function loadNotifications() {
        try {
            const response = await fetch('/api/notifications/');
            if (!response.ok) return;
            const data = await response.json();
            
            if (data.notifications && data.notifications.length > 0) {
                notificationBadge.style.display = 'block';
                notificationList.innerHTML = '';
                data.notifications.forEach(notif => {
                    const item = document.createElement('div');
                    item.className = 'notification-item';
                    item.innerHTML = `
                        <span class="notification-icon">
                            <img src="/static/myapp/images/calendar.png" alt="Календарь">
                        </span>
                        <p class="notification-text">${escapeHtml(notif.message)}</p>
                    `;
                    notificationList.appendChild(item);
                });
            } else {
                notificationBadge.style.display = 'none';
                notificationList.innerHTML = `
                    <div class="notification-empty">
                        <span class="notification-icon">
                            <img src="/static/myapp/images/mail.png" alt="Нет уведомлений">
                        </span>
                        <p class="notification-text">Сейчас у вас нет новых уведомлений</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Ошибка уведомлений:', error);
        }
    }
    
    notificationBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        
        if (!isOpen) {
            await loadNotifications();
            notificationDropdown.style.display = 'block';
            isOpen = true;
        } else {
            notificationDropdown.style.display = 'none';
            isOpen = false;
        }
    });
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.notification-wrapper')) {
            notificationDropdown.style.display = 'none';
            isOpen = false;
        }
    });
    
    loadNotifications();
});