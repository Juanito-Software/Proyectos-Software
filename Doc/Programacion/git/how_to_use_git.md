-Configuración INICIAL repositorio-

iniciar repositorio: 	git init
añadir origen:	  	git remote add "origen" "url_repositorio"			ej: git remote add gitlab https://gitlab.com/JuanBP97/Juan_repositorio.git
eliminar origen:  	git remote remove "origen"
ver datos origen:	git remote show "origen"
ver rama actual:  	git Branch
ver estado:		git status 


-Subir al repositorio-PUSH

git add .
git commit -m "Primer commit"


git push --force github master
git push --force gitlab master


-Bajar del repositorio-PULL

git pull github master

git pull gitlab master


-CLONAR-
git clone https://github.com/JuanBP12/Juan_repositorio.git
git clone https://gitlab.com/juanbpgitlabs/juanito_dam2t_repository2.git




----RAMAS-----



Perfecto Juan, ahora vamos a hacerlo práctico de verdad.

Te voy a explicar cómo crear exactamente esa estructura trabajando tú solo, sin complicaciones y sin teoría innecesaria.

🎯 Situación actual

Ahora mismo tienes:

main

Y trabajas todo ahí.

Vamos a empezar a trabajar con ramas de forma profesional.

🧠 Caso real: quieres hacer el login
1️⃣ Crear una rama nueva

Estando en tu proyecto:

git checkout -b feature/login-system

¿Qué hace esto?

checkout -b crea una rama nueva

Te cambia automáticamente a esa rama

Ahora ya no estás en main.

2️⃣ Trabajas normalmente

Editas archivos.

Luego:

git add .
git commit -m "Añade sistema de login básico"

Y si quieres subirla a GitHub:

git push origin feature/login-system

Ahora en GitHub existe esa rama.

3️⃣ Volver a main

Cuando termines el login:

git checkout main
4️⃣ Mezclar la rama en main
git merge feature/login-system

Ahora main ya tiene el login.

Y puedes borrar la rama si quieres:

git branch -d feature/login-system
🧱 Lo mismo con inventory
git checkout -b feature/inventory

Trabajas → commit → push → vuelves a main → merge.

🛠️ Para un bug (ejemplo save-bug)

Desde main:

git checkout main
git checkout -b fix/save-bug

Arreglas el bug → commit → merge → borrar rama.

📊 Visualmente queda así

Antes:

main

Después:

main
 ├── feature/login-system
 ├── feature/inventory
 └── fix/save-bug

Pero ojo:

Esas ramas no se quedan eternamente.
Viven poco y mueren rápido.

Eso es importante.

🔥 Consejo profesional moderno

No hagas ramas que vivan semanas.

Haz:

Rama

Trabajo pequeño

Merge rápido

Borrar

Eso es flujo moderno real (trunk-based con ramas cortas).

🧠 Extra importante (detalle que muchos no saben)

Antes de crear una rama nueva, asegúrate de que main esté actualizado:

git checkout main
git pull origin main
git checkout -b feature/lo-que-sea

Esto evita conflictos raros.


Lo más realista sería:

✔ versión simple mejor:
main
develop
feature/*

Sin release/hotfix salvo que crezca mucho


---


🧠 1. Estructura base de Git Flow

Tienes estas ramas principales:

main        → versión estable (producción)
develop     → integración de desarrollo

Y ramas auxiliares:

feature/*   → nuevas funcionalidades
release/*   → preparación de versión
hotfix/*    → arreglos urgentes en producción
🔧 2. Flujo real paso a paso
🚀 1. Empezar feature (ej: PASV)
git checkout develop
git checkout -b feature/pasv-mode

Trabajas ahí.

📦 2. Commit usando Conventional Commits
feat: implement PASV mode support
🔀 3. Terminar feature
git checkout develop
git merge feature/pasv-mode
🧪 4. Preparar release

Cuando ya está “listo para versión”:

git checkout -b release/1.0.0

Aquí solo:

bugs pequeños
docs
ajustes finales
🏁 5. Pasar a producción
git checkout main
git merge release/1.0.0

y luego:

git tag 1.0.0
🔥 6. Hotfix (crítico en producción)

Si hay un bug en main:

git checkout -b hotfix/fix-path-bug main

Arreglas:

fix: correct directory traversal vulnerability in CWD

Luego:

git checkout main
git merge hotfix/fix-path-bug
git tag 1.0.1

Y también:

git checkout develop
git merge hotfix/fix-path-bug
🧠 3. Visual mental del sistema
main -----------o--------o----o (releases)
                 \      /
develop ----o----o----o----o----o
              \      /
feature        feature branches
⚖️ 4. Cuándo usar Git Flow (y cuándo NO)
✔ Útil cuando:
proyectos con versiones (v1, v2…)
software “estable”
equipos grandes
releases controladas


---


Commits:

🔧 Tipos más usados
🚀 feat

Nueva funcionalidad

feat: add PASV mode support
🐛 fix

Corrección de bugs

fix: resolve file path handling in CWD command
📚 docs

Cambios en documentación

docs: update README with FileZilla usage instructions
🔧 refactor

Cambios internos sin cambiar comportamiento

refactor: simplify FTP command parser logic
🧪 test

Añadir o modificar tests

test: add unit tests for path validation
⚙️ chore

Tareas internas (build, config, limpieza)

chore: update Cargo.toml dependencies
🚨 style (menos importante en Rust)

Formato, espacios, etc.

style: format code with rustfmt


| tipo     | uso                               |
| -------- | --------------------------------- |
| feat     | nueva funcionalidad               |
| fix      | bug                               |
| refactor | cambios sin cambiar funcionalidad |
| chore    | mantenimiento                     |
| docs     | documentación                     |
| test     | tests                             |
| archive  | mover a archive/                  |

