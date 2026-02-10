/**
 * Script helper para obtener el token de acceso de DLive
 * 
 * INSTRUCCIONES:
 * 1. Abre tu canal de DLive en el navegador (https://dlive.tv/tu_usuario)
 * 2. Abre la consola del navegador (F12)
 * 3. Copia y pega este código en la consola
 * 4. El script buscará automáticamente el token y lo mostrará
 */

(function() {
  console.log('🔍 Buscando token de DLive...');
  
  // Método 1: Buscar en Local Storage
  console.log('\n📦 Buscando en Local Storage...');
  let found = false;
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    const value = localStorage.getItem(key);
    if (value && (value.includes('Bearer') || value.includes('eyJ') || key.toLowerCase().includes('token') || key.toLowerCase().includes('auth'))) {
      console.log(`✅ Encontrado en Local Storage - Key: ${key}`);
      console.log(`Token: ${value}`);
      found = true;
    }
  }
  
  // Método 2: Buscar en Session Storage
  console.log('\n📦 Buscando en Session Storage...');
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    const value = sessionStorage.getItem(key);
    if (value && (value.includes('Bearer') || value.includes('eyJ') || key.toLowerCase().includes('token') || key.toLowerCase().includes('auth'))) {
      console.log(`✅ Encontrado en Session Storage - Key: ${key}`);
      console.log(`Token: ${value}`);
      found = true;
    }
  }
  
  // Método 3: Interceptar peticiones de red
  console.log('\n🌐 Interceptando peticiones de red...');
  console.log('💡 Recarga la página (F5) y observa las peticiones a api.dlive.tv o api-ws.dlive.tv');
  console.log('💡 Busca en la pestaña Network > Headers > Authorization');
  
  // Método 4: Buscar en cookies
  console.log('\n🍪 Buscando en Cookies...');
  document.cookie.split(';').forEach(cookie => {
    const [key, value] = cookie.trim().split('=');
    if (key && (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth'))) {
      console.log(`✅ Encontrado en Cookies - Key: ${key}`);
      console.log(`Token: ${value}`);
      found = true;
    }
  });
  
  // Método 5: Buscar en window object
  console.log('\n🔎 Buscando en objetos globales...');
  const searchInObject = (obj, path = '') => {
    for (const key in obj) {
      try {
        const value = obj[key];
        const currentPath = path ? `${path}.${key}` : key;
        
        if (typeof value === 'string' && (value.includes('Bearer') || value.includes('eyJ') || value.length > 50)) {
          if (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth') || key.toLowerCase().includes('access')) {
            console.log(`✅ Posible token encontrado en: ${currentPath}`);
            console.log(`Token: ${value.substring(0, 100)}...`);
            found = true;
          }
        } else if (typeof value === 'object' && value !== null && path.split('.').length < 3) {
          searchInObject(value, currentPath);
        }
      } catch (e) {
        // Ignorar errores de acceso
      }
    }
  };
  
  // Buscar en window.__APOLLO_STATE__ o window.__INITIAL_STATE__ que suelen tener tokens
  if (window.__APOLLO_STATE__) {
    searchInObject(window.__APOLLO_STATE__, '__APOLLO_STATE__');
  }
  if (window.__INITIAL_STATE__) {
    searchInObject(window.__INITIAL_STATE__, '__INITIAL_STATE__');
  }
  if (window.apolloClient) {
    searchInObject(window.apolloClient, 'apolloClient');
  }
  
  if (!found) {
    console.log('\n❌ No se encontró token automáticamente.');
    console.log('\n📋 INSTRUCCIONES MANUALES:');
    console.log('1. Abre la pestaña "Network" (Red) en las herramientas de desarrollador');
    console.log('2. Recarga la página (F5)');
    console.log('3. Busca peticiones a "api.dlive.tv" o "api-ws.dlive.tv"');
    console.log('4. Haz clic en una petición');
    console.log('5. Ve a la pestaña "Headers" (Encabezados)');
    console.log('6. Busca "Authorization" o "authorization" en Request Headers');
    console.log('7. Copia el valor (puede empezar con "Bearer " o ser directamente el token)');
    console.log('\n💡 Si el token empieza con "Bearer ", copia solo la parte después de "Bearer "');
  } else {
    console.log('\n✅ Token encontrado! Copia el valor y añádelo a tu .env como:');
    console.log('DLIVE_ACCESS_TOKEN=el_token_aqui');
  }
})();

