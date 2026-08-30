import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cada test empieza con el DOM y el almacenamiento vacíos: si no, un test que
// deja una sesión guardada hace pasar (o fallar) al siguiente, y el resultado
// depende del orden de ejecución.
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});
