document.addEventListener('DOMContentLoaded', function() {
    const notificationBadge = document.getElementById('notification-badge');
    const notificationList = document.querySelector('.notification-list');
    const notificationBell = document.querySelector('.notification-bell');
    
    // Intervalo de atualização (a cada 1 minuto)
    const updateInterval = 60 * 1000;
    
    // Função para obter ícone baseado no tipo de notificação e prioridade
    function getNotificationStyle(priority) {
        const styles = {
            'urgent': {
                icon: 'fas fa-exclamation-circle',
                bgClass: 'bg-danger',
                textClass: 'text-danger'
            },
            'high': {
                icon: 'fas fa-exclamation-triangle',
                bgClass: 'bg-warning',
                textClass: 'text-warning'
            },
            'medium': {
                icon: 'fas fa-info-circle',
                bgClass: 'bg-info',
                textClass: 'text-info'
            },
            'low': {
                icon: 'fas fa-bell',
                bgClass: 'bg-success',
                textClass: 'text-success'
            },
            'normal': {
                icon: 'fas fa-bell',
                bgClass: 'bg-primary',
                textClass: 'text-primary'
            }
        };
        return styles[priority] || styles.normal;
    }
    
    // Função para atualizar o contador de notificações
    function updateNotificationCount() {
        fetch('/notifications/api/unread-count')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    notificationBadge.style.display = 'block';
                    notificationBadge.textContent = data.count > 99 ? '99+' : data.count;
                    notificationBadge.className = `position-absolute top-0 start-100 translate-middle badge rounded-pill ${getNotificationStyle(data.highest_priority).bgClass}`;
                } else {
                    notificationBadge.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Erro ao buscar contagem de notificações:', error);
            });
    }
    
    // Função para carregar as notificações não lidas no dropdown
    function loadNotifications() {
        if (!notificationList) return;     
        fetch('/notifications/api/unread')
        .then(response => response.json())
        .then(data => {
            notificationList.innerHTML = '';
            
            if (data.notifications && data.notifications.length > 0) {
                data.notifications.forEach(notification => {
                    const style = getNotificationStyle(notification.priority);
                    const notifDate = new Date(notification.created_at).toLocaleString();
                    
                    const item = document.createElement('a');
                    item.href = '/notifications';
                    item.className = `list-group-item list-group-item-action border-bottom`;
                    
                    item.innerHTML = `
                        <div class="row align-items-center">
                            <div class="col-auto">
                                <div class="icon-shape icon-xs ${style.bgClass} text-white rounded-circle">
                                    <i class="${getCategoryIcon(notification.category)}"></i>
                                </div>
                            </div>
                            <div class="col ps-0 ms-2">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h4 class="h6 mb-0 text-small">${notification.title}</h4>
                                        <span class="badge ${style.bgClass} ms-2">${notification.priority}</span>
                                    </div>
                                    <div class="text-end">
                                        <small class="text-muted">${notifDate}</small>
                                    </div>
                                </div>
                                <p class="font-small mt-1 mb-0">${notification.message}</p>
                            </div>
                        </div>
                    `;
                    
                    notificationList.appendChild(item);
                });
            } else {
                // ... resto do código ...
            }
        });

// Função auxiliar para obter ícone baseado na categoria
function getCategoryIcon(category) {
const icons = {
    'document': 'fas fa-file-alt',
    'contract': 'fas fa-file-contract',
    'maintenance': 'fas fa-tools',
    'financial': 'fas fa-money-bill-wave',
    'property': 'fas fa-home',
    'default': 'fas fa-bell'
};
return icons[category] || icons.default;
}
    
    // Inicializar
    if (notificationBadge) {
        updateNotificationCount();
        setInterval(updateNotificationCount, updateInterval);
    }
    
    // Carregar notificações ao clicar no sino
    if (notificationBell) {
        notificationBell.addEventListener('click', function() {
            loadNotifications();
        });
    }
});