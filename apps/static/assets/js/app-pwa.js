/**
 * Script para inicialização da PWA e funcionalidades offline
 */

// Verificar o status da conexão e exibir indicadores
const offlineIndicator = document.getElementById('offline-indicator');
const syncPendingIndicator = document.getElementById('sync-pending');

// Exibir indicador de modo offline quando não houver conexão
function updateOnlineStatus() {
    if (!navigator.onLine) {
        document.body.classList.add('is-offline');
        if (offlineIndicator) {
            offlineIndicator.classList.remove('d-none');
        }
    } else {
        document.body.classList.remove('is-offline');
        if (offlineIndicator) {
            offlineIndicator.classList.add('d-none');
        }
    }
}

// Inicializar os eventos de status de conexão
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
updateOnlineStatus();

// Registrar o service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(function(registration) {
                console.log('Service Worker registrado com sucesso:', registration.scope);
                
                // Verificar e mostrar aviso de nova versão disponível
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateAvailable();
                        }
                    });
                });
            })
            .catch(function(error) {
                console.log('Falha ao registrar Service Worker:', error);
            });
            
        // Verificar atualizações a cada hora
        setInterval(() => {
            navigator.serviceWorker.getRegistration().then(registration => {
                if (registration) {
                    registration.update();
                }
            });
        }, 60 * 60 * 1000);
    });
    
    // Lidar com mensagens do service worker
    navigator.serviceWorker.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'SYNC_COMPLETE') {
            showSyncComplete(event.data.count);
            
            if (syncPendingIndicator) {
                syncPendingIndicator.classList.add('d-none');
            }
        }
        
        if (event.data && event.data.type === 'SYNC_PENDING') {
            if (syncPendingIndicator) {
                syncPendingIndicator.classList.remove('d-none');
                const countBadge = syncPendingIndicator.querySelector('.badge');
                if (countBadge) {
                    countBadge.textContent = event.data.count;
                }
            }
        }
    });
}

// Mostrar notificação de atualização disponível
function showUpdateAvailable() {
    const notyf = new Notyf({
        duration: 0,
        dismissible: true,
        position: {
            x: 'right',
            y: 'bottom',
        },
        types: [
            {
                type: 'update',
                background: '#262b40',
                icon: {
                    className: 'fas fa-cloud-download-alt',
                    tagName: 'i',
                    color: 'white'
                }
            }
        ]
    });
    
    const notification = notyf.open({
        type: 'update',
        message: 'Nova versão disponível! <button class="btn btn-sm btn-primary ms-3 update-btn">Atualizar agora</button>'
    });
    
    // Adicionar listener para o botão de atualização
    setTimeout(() => {
        const updateBtn = document.querySelector('.update-btn');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => {
                window.location.reload();
                notification.dismiss();
            });
        }
    }, 100);
}

// Mostrar notificação de sincronização completa
function showSyncComplete(count) {
    if (!count) return;
    
    const notyf = new Notyf({
        duration: 5000,
        position: {
            x: 'right',
            y: 'bottom',
        },
        types: [
            {
                type: 'sync',
                background: '#10b981',
                icon: {
                    className: 'fas fa-check-circle',
                    tagName: 'i',
                    color: 'white'
                }
            }
        ]
    });
    
    notyf.open({
        type: 'sync',
        message: `${count} ${count === 1 ? 'item sincronizado' : 'itens sincronizados'} com sucesso!`
    });
}

// Salvar dados quando offline
function saveOfflineData(key, data) {
    if ('localStorage' in window) {
        try {
            const pendingData = JSON.parse(localStorage.getItem('pendingData') || '[]');
            pendingData.push({
                id: Date.now().toString(),
                key: key,
                data: data,
                timestamp: new Date().toISOString()
            });
            
            localStorage.setItem('pendingData', JSON.stringify(pendingData));
            
            // Agendar sincronização quando a conexão for restaurada
            if ('serviceWorker' in navigator && 'SyncManager' in window) {
                navigator.serviceWorker.ready
                    .then(registration => {
                        registration.sync.register('sync-dados-pendentes');
                    })
                    .catch(err => {
                        console.error('Falha ao registrar sync:', err);
                    });
            }
            
            // Mostrar indicador de dados pendentes
            if (syncPendingIndicator) {
                syncPendingIndicator.classList.remove('d-none');
                const countBadge = syncPendingIndicator.querySelector('.badge');
                if (countBadge) {
                    countBadge.textContent = pendingData.length;
                }
            }
            
            return true;
        } catch (e) {
            console.error('Erro ao salvar dados offline:', e);
            return false;
        }
    }
    return false;
}

// Obter dados pendentes
function getPendingData() {
    if ('localStorage' in window) {
        try {
            return JSON.parse(localStorage.getItem('pendingData') || '[]');
        } catch (e) {
            console.error('Erro ao obter dados pendentes:', e);
            return [];
        }
    }
    return [];
}

// Remover dados pendentes
function removePendingData(id) {
    if ('localStorage' in window) {
        try {
            const pendingData = JSON.parse(localStorage.getItem('pendingData') || '[]');
            const newPendingData = pendingData.filter(item => item.id !== id);
            
            localStorage.setItem('pendingData', JSON.stringify(newPendingData));
            
            // Atualizar indicador
            if (syncPendingIndicator && newPendingData.length === 0) {
                syncPendingIndicator.classList.add('d-none');
            } else if (syncPendingIndicator) {
                const countBadge = syncPendingIndicator.querySelector('.badge');
                if (countBadge) {
                    countBadge.textContent = newPendingData.length;
                }
            }
            
            return true;
        } catch (e) {
            console.error('Erro ao remover dados pendentes:', e);
            return false;
        }
    }
    return false;
}

// Verificar se a instalação é possível
let deferredPrompt;
const pwaInstallButton = document.getElementById('pwa-install-btn');

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    if (pwaInstallButton) {
        pwaInstallButton.classList.remove('d-none');
        
        pwaInstallButton.addEventListener('click', (e) => {
            pwaInstallButton.classList.add('d-none');
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('Usuário aceitou a instalação do PWA');
                } else {
                    console.log('Usuário recusou a instalação do PWA');
                }
                deferredPrompt = null;
            });
        });
    }
});

// Verificar se já está instalado
window.addEventListener('appinstalled', () => {
    if (pwaInstallButton) {
        pwaInstallButton.classList.add('d-none');
    }
    deferredPrompt = null;
    console.log('PWA instalado com sucesso');
});

// Detectar se está executando como aplicativo instalado
if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true) {
    document.body.classList.add('pwa-installed');
    
    // Ocultar botão de instalação se já estiver instalado
    if (pwaInstallButton) {
        pwaInstallButton.classList.add('d-none');
    }
}

// Exportar funções para uso global
window.appPWA = {
    saveOfflineData,
    getPendingData,
    removePendingData,
    isOnline: () => navigator.onLine
};