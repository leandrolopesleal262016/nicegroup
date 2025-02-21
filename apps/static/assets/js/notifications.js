/**
 * Gerenciamento de notificações
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos
    const notificationBadge = document.getElementById('notification-badge');
    const notificationList = document.querySelector('.notification-list');
    const notificationBell = document.querySelector('.notification-bell');
    
    // Intervalo de atualização (a cada 1 minuto)
    const updateInterval = 60 * 1000;
    
    // Função para atualizar o contador de notificações
    function updateNotificationCount() {
        fetch('/notifications/api/unread-count')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    notificationBadge.style.display = 'block';
                    notificationBadge.textContent = data.count > 99 ? '99+' : data.count;
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
                        const notifIcon = getNotificationIcon(notification.notif_type);
                        const notifDate = new Date(notification.created_at).toLocaleString();
                        
                        const item = document.createElement('a');
                        item.href = notification.link || '/notifications';
                        item.className = 'list-group-item list-group-item-action border-bottom';
                        
                        item.innerHTML = `
                            <div class="row align-items-center">
                                <div class="col-auto">
                                    <div class="icon-shape icon-xs ${notifIcon.bgClass} text-white rounded-circle">
                                        <i class="${notifIcon.icon}"></i>
                                    </div>
                                </div>
                                <div class="col ps-0 ms-2">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <h4 class="h6 mb-0 text-small">${notification.title}</h4>
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
                    const emptyItem = document.createElement('div');
                    emptyItem.className = 'text-center p-4';
                    emptyItem.innerHTML = `
                        <i class="fas fa-bell-slash fa-2x text-muted mb-3"></i>
                        <p class="text-muted">Nenhuma notificação não lida</p>
                    `;
                    notificationList.appendChild(emptyItem);
                }
            })
            .catch(error => {
                console.error('Erro ao carregar notificações:', error);
            });
    }
    
    // Função para obter ícone baseado no tipo de notificação
    function getNotificationIcon(type) {
        switch (type) {
            case 'contract':
                return { icon: 'fas fa-file-contract', bgClass: 'bg-primary' };
            case 'document':
                return { icon: 'fas fa-file-alt', bgClass: 'bg-warning' };
            case 'maintenance':
                return { icon: 'fas fa-tools', bgClass: 'bg-info' };
            case 'financial':
                return { icon: 'fas fa-money-bill-wave', bgClass: 'bg-success' };
            case 'property':
                return { icon: 'fas fa-home', bgClass: 'bg-secondary' };
            default:
                return { icon: 'fas fa-bell', bgClass: 'bg-gray-500' };
        }
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