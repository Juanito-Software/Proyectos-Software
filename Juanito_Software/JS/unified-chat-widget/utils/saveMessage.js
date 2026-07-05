import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

//Para HTTP
/*
export function appendLatestJson(messages) {
  try {
        const filePath = path.join(__dirname, '../messages/latest.json'); // Asegúrate de usar ruta relativa correcta
        fs.writeFileSync(filePath, JSON.stringify(messages, null, 2), 'utf8');
        console.log(`✅ Archivo actualizado correctamente en: ${filePath}`);
    } catch (error) {
        console.error(`❌ Error al guardar latest.json: ${error.message}`);
    }
}
*/
