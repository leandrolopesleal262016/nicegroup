// Verifica se o aplicativo está online ou offline
function isOnline() {
    return navigator.onLine;
}

// Armazena propriedades criadas offline
function savePropertyOffline(propertyData) {
    const offlineProperties = getOfflineProperties();
    offlineProperties.push({
        data: propertyData,
        timestamp: new Date().toISOString()
    });
    localStorage.setItem('offlineProperties', JSON.stringify(offlineProperties));
    
    // Registra para sincronização quando online
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready
            .then(registration => {
                registration.sync.register('sync-new-properties');
            });
    }
}

// Recupera propriedades armazenadas offline
function getOfflineProperties() {
    const data = localStorage.getItem('offlineProperties');
    return data ? JSON.parse(data) : [];
}

// Armazena documentos criados offline
function saveDocumentOffline(documentData) {
    const offlineDocuments = getOfflineDocuments();
    offlineDocuments.push({
        data: documentData,
        timestamp: new Date().toISOString()
    });
    localStorage.setItem('offlineDocuments', JSON.stringify(offlineDocuments));
    
    // Registra para sincronização quando online
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready
            .then(registration => {
                registration.sync.register('sync-new-documents');
            });
    }
}

// Recupera documentos armazenados offline
function getOfflineDocuments() {
    const data = localStorage.getItem('offlineDocuments');
    return data ? JSON.parse(data) : [];
}

// Armazena transações criadas offline
function saveTransactionOffline(transactionData) {
    const offlineTransactions = getOfflineTransactions();
    offlineTransactions.push({
        data: transactionData,
        timestamp: new Date().toISOString()
    });
    localStorage.setItem('offlineTransactions', JSON.stringify(offlineTransactions));
    
    // Registra para sincronização quando online
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready
            .then(registration => {
                registration.sync.register('sync-new-transactions');
            });
    }
}

// Recupera transações armazenadas offline
function getOfflineTransactions() {
    const data = localStorage.getItem('offlineTransactions');
    return data ? JSON.parse(data) : [];
}

// Inicializa recursos offline
document.addEventListener('DOMContentLoaded', function() {
    // Adiciona manipuladores de eventos para formulários
    const propertyForm = document.querySelector('form[action*="add_property"]');
    if (propertyForm) {
        propertyForm.addEventListener('submit', function(event) {
            if (!isOnline()) {
                event.preventDefault();
                const formData = new FormData(propertyForm);
                const propertyData = {};
                
                for (const [key, value] of formData.entries()) {
                    propertyData[key] = value;
                }
                
                savePropertyOffline(propertyData);
                
                // Notifica o usuário
                alert('Você está offline. O imóvel será salvo localmente e sincronizado quando houver conexão.');
                
                // Redireciona para a lista de propriedades
                window.location.href = '/properties';
            }
        });
    }
    
    // Adicionar manipuladores similares para formulários de documentos e transações
});