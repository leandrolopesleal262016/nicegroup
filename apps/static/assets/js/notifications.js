document.addEventListener('DOMContentLoaded', function() {
    // Referências aos elementos
    const notificationBell = document.querySelector('.notification-bell');
    const notificationContainer = document.querySelector('.notification-container');
    
    // Função para formatar a data
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Função para obter ícone baseado na categoria
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
    
    // Função para obter estilo baseado na prioridade
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
    
    // Função para carregar notificações via AJAX
    function loadNotifications() {
        if (!notificationContainer) return;
        
        // Mostrar indicador de carregamento
        notificationContainer.innerHTML = '<div class="text-center py-4"><div class="spinner-border spinner-border-sm text-primary" role="status"></div></div>';
        
        fetch('/api/notificacoes')
            .then(response => response.json())
            .then(data => {
                // Limpar container
                notificationContainer.innerHTML = '';
                
                // Verificar se há notificações
                if (data && data.length > 0) {
                    // Agrupar por prioridade
                    const grouped = {
                        urgent: [],
                        high: [],
                        medium: [],
                        low: []
                    };
                    
                    data.forEach(notif => {
                        if (grouped[notif.priority]) {
                            grouped[notif.priority].push(notif);
                        }
                    });
                    
                    // Renderizar notificações urgentes
                    if (grouped.urgent.length > 0) {
                        const header = document.createElement('div');
                        header.className = 'notification-header border-bottom';
                        header.innerHTML = '<span class="small text-danger fw-bold px-3 py-2 d-block">Urgentes</span>';
                        notificationContainer.appendChild(header);
                        
                        grouped.urgent.slice(0, 3).forEach(notif => {
                            const item = createNotificationItem(notif, 'urgent');
                            notificationContainer.appendChild(item);
                        });
                    }
                    
                    // Renderizar notificações de alta prioridade
                    if (grouped.high.length > 0) {
                        const header = document.createElement('div');
                        header.className = 'notification-header border-bottom';
                        header.innerHTML = '<span class="small text-warning fw-bold px-3 py-2 d-block">Alta Prioridade</span>';
                        notificationContainer.appendChild(header);
                        
                        grouped.high.slice(0, 2).forEach(notif => {
                            const item = createNotificationItem(notif, 'high');
                            notificationContainer.appendChild(item);
                        });
                    }
                    
                    // Se não há notificações de alta prioridade
                    if (grouped.urgent.length === 0 && grouped.high.length === 0) {
                        const emptyNotif = document.createElement('a');
                        emptyNotif.href = "#";
                        emptyNotif.className = "text-center text-gray-500 fw-bold border-bottom border-light py-3";
                        emptyNotif.innerText = "Nenhuma notificação prioritária";
                        notificationContainer.appendChild(emptyNotif);
                    }
                } else {
                    // Sem notificações
                    const emptyNotif = document.createElement('a');
                    emptyNotif.href = "#";
                    emptyNotif.className = "text-center text-gray-500 fw-bold border-bottom border-light py-3";
                    emptyNotif.innerText = "Nenhuma notificação";
                    notificationContainer.appendChild(emptyNotif);
                }
                
                // Adicionar link para todas as notificações
                const viewAllLink = document.createElement('a');
                viewAllLink.href = "/notificacoes";
                viewAllLink.className = "dropdown-item text-center fw-bold py-3";
                viewAllLink.innerText = "Visualizar todas";
                
                if (data.length > 0) {
                    const badge = document.createElement('span');
                    badge.className = "badge bg-primary ms-2";
                    badge.innerText = data.length;
                    viewAllLink.appendChild(badge);
                }
                
                notificationContainer.appendChild(viewAllLink);
            })
            .catch(error => {
                console.error('Erro ao carregar notificações:', error);
                notificationContainer.innerHTML = '<a href="#" class="text-center text-danger fw-bold border-bottom border-light py-3">Erro ao carregar notificações</a>';
                
                const viewAllLink = document.createElement('a');
                viewAllLink.href = "/notificacoes";
                viewAllLink.className = "dropdown-item text-center fw-bold py-3";
                viewAllLink.innerText = "Visualizar todas";
                notificationContainer.appendChild(viewAllLink);
            });
    }
    
    // Função para criar um item de notificação
    function createNotificationItem(notification, priority) {
        const style = getNotificationStyle(priority);
        const item = document.createElement('a');
        item.href = "/notificacoes";
        item.className = "list-group-item list-group-item-action border-0 border-bottom py-3 px-3";
        
        item.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="icon-shape icon-xs ${style.bgClass} text-white rounded-circle me-2">
                    <i class="${style.icon}"></i>
                </div>
                <div>
                    <span class="fw-bold">${notification.title}</span>
                    <p class="small text-gray-500 mb-0">${notification.message}</p>
                </div>
            </div>
        `;
        
        return item;
    }
    
    // Adicionar evento de clique ao sino para carregar notificações
    if (notificationBell) {
        notificationBell.addEventListener('click', function() {
            loadNotifications();
        });
    }
});