# Guía para migrar a MongoDB

Si hace tiempo que no usas MongoDB, aquí tienes los pasos concretos para sustituir `store.js` por Mongoose.

---

## 1. Instalar dependencias

En la carpeta `server/`:

```bash
cd server
npm install mongoose
```

---

## 2. Crear cuenta en MongoDB Atlas (gratis)

1. Entra en [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Crea cuenta o inicia sesión
3. Crea un **cluster gratis** (M0)
4. Crea un usuario de base de datos: **Username** y **Password** (guárdalos)
5. En **Network Access**, añade tu IP o usa `0.0.0.0/0` para permitir cualquiera (solo para desarrollo)
6. En el cluster, clic en **Connect** → **Connect your application** → copia la URI, algo como:
   ```
   mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/
   ```
7. Añade el nombre de la base al final: `mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/taskhub`

---

## 3. Variables de entorno

En `server/`, crea un archivo `.env`:

```
MONGODB_URI=mongodb+srv://tuUsuario:tuPassword@cluster0.xxxxx.mongodb.net/taskhub
JWT_SECRET=una-clave-secreta-muy-larga-y-aleatoria
```

O para probar en local (con MongoDB instalado):

```
MONGODB_URI=mongodb://localhost:27017/taskhub
```

---

## 4. Instalar dotenv (para leer .env)

```bash
cd server
npm install dotenv
```

---

## 5. Modelos Mongoose

Crea `server/models/Task.js`:

```javascript
import mongoose from 'mongoose';

const taskSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  completed: { type: Boolean, default: false },
  userId: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
});

export default mongoose.model('Task', taskSchema);
```

Y `server/models/User.js` (si usas auth):

```javascript
import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  passwordHash: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
});

export default mongoose.model('User', userSchema);
```

---

## 6. Conectar Mongoose en `server/index.js`

```javascript
import dotenv from 'dotenv';
import mongoose from 'mongoose';

dotenv.config();

// Antes de app.listen()
try {
  await mongoose.connect(process.env.MONGODB_URI);
  console.log('Conectado a MongoDB');
} catch (err) {
  console.error('Error conectando a MongoDB:', err);
}
```

---

## 7. Sustituir funciones en `store.js`

En lugar de leer/escribir JSON, usas el modelo:

```javascript
import Task from './models/Task.js';

export async function getAllTasks(userId) {
  return Task.find({ userId }).sort({ updatedAt: -1 }).lean();
}

export async function getTaskById(id, userId) {
  return Task.findOne({ _id: id, userId }).lean();
}

export async function createTask(task) {
  const created = await Task.create({
    ...task,
    updatedAt: new Date(),
  });
  return created.toObject();
}

export async function updateTask(id, userId, updates) {
  const doc = await Task.findOneAndUpdate(
    { _id: id, userId },
    { ...updates, updatedAt: new Date() },
    { new: true }
  );
  return doc?.toObject() ?? null;
}

export async function deleteTask(id, userId) {
  const result = await Task.deleteOne({ _id: id, userId });
  return result.deletedCount > 0;
}
```

**Nota**: Mongoose usa `_id` (ObjectId) en lugar de `id` (string). Puedes agregar un virtual para exponer `id` o adaptar el frontend para usar `_id`.

---

## 8. Ajustar rutas para usar `_id`

En las rutas, el `id` de la URL será el `_id` de MongoDB. Mongoose lo acepta directamente en `findById`, `findByIdAndUpdate`, etc.

---

## Resumen rápido

| Antes (JSON) | Después (MongoDB) |
|--------------|-------------------|
| `fs.readFileSync` | `Task.find()` |
| `fs.writeFileSync` | `Task.create()` / `Task.updateOne()` |
| `crypto.randomUUID()` para id | `_id` automático de MongoDB |

---

## MongoDB local (sin Atlas)

Si prefieres no usar la nube:

1. Instala MongoDB Community: [mongodb.com/docs/manual/installation](https://www.mongodb.com/docs/manual/installation/)
2. Inicia el servicio
3. Usa `MONGODB_URI=mongodb://localhost:27017/taskhub`
