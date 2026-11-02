/**
 * Punto de entrada del cliente: monta `<App />` en el `#root` de index.html.
 *
 * `StrictMode` solo actúa en desarrollo: monta los componentes dos veces para
 * destapar efectos que no se limpian bien. No afecta al build de producción.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
