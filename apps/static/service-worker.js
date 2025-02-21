// Nome do cache
const CACHE_NAME = 'nice-group-cache-v1';

// Recursos para cache
const urlsToCache = [
  '/',
  '/index',
  '/static/assets/css/volt.css',
  '/static/assets/js/volt.js',
  '/static/assets/vendor/bootstrap/dist/js/bootstrap.min.js',
  '/static/assets/vendor/jquery/dist/jquery.min.js',
  '/static/assets/vendor/popper.js/dist/umd/popper.min.js',
  '/static/assets/vendor/sweetalert2/dist/sweetalert2.min.js',
  '/static/assets/vendor/notyf/notyf.min.js',
  '/static/assets/img/brand/light.svg',
  '/static/assets/img/brand/dark.svg',
  '/static/assets/img/favicon/favicon.ico',
  // Adicione outros recursos estáticos importantes
];

// Instalação do service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Interceptação de requisições de rede
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - retorna a resposta do cache
        if (response) {
          return response;
        }

        // Cria um clone da requisição
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest)
          .then(response => {
            // Verifica se a resposta é válida
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Cria um clone da resposta
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // Se falhar a conexão e for uma página, retorna uma página offline
            if (event.request.url.includes('/index') || 
                event.request.url.includes('/properties') ||
                event.request.url.includes('/property/')) {
              return caches.match('/static/offline.html');
            }
          });
      })
  );
});

// Atualização do cache
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            // Exclui caches antigos
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Sincronização em segundo plano
self.addEventListener('sync', event => {
  if (event.tag === 'sync-new-properties') {
    event.waitUntil(syncNewProperties());
  } else if (event.tag === 'sync-new-documents') {
    event.waitUntil(syncNewDocuments());
  } else if (event.tag === 'sync-new-transactions') {
    event.waitUntil(syncNewTransactions());
  }
});

// Função para sincronizar novos imóveis
function syncNewProperties() {
  // Lógica para sincronizar novos imóveis
  return fetch('/api/sync-properties', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      data: getOfflineProperties()
    })
  })
  .then(response => {
    if (response.ok) {
      // Limpa dados offline após sincronização
      clearOfflineProperties();
    }
  });
}

// Funções auxiliares para armazenamento offline
function getOfflineProperties() {
  // Recupera dados do localStorage
  const data = localStorage.getItem('offlineProperties');
  return data ? JSON.parse(data) : [];
}

function clearOfflineProperties() {
  localStorage.removeItem('offlineProperties');
}

// Notificações push
self.addEventListener('push', event => {
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: '/static/assets/img/brand/icon-192x192.png',
    badge: '/static/assets/img/brand/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url
    }
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Clique na notificação
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});