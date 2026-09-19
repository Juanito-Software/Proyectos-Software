# Cómo usar Git — flujo canónico del repositorio

> **Documentación canónica del flujo Git** de Proyectos-Software (© Juanito
> Software). El flujo real del repo se apoya en dos aliases definidos en
> `~/.gitconfig` — **`git nueva`** (crea rama desde `main` fresco y poda las ya
> integradas) y **`git subir`** (push + PR + auto-merge; el argumento es el
> método de integración, no una rama). El resumen vigente empieza en la sección
> **_«Tu día a día»_**. Las secciones anteriores a ella son el **flujo antiguo**
> (commits directos, `checkout -b`/`merge` manuales, Git Flow): se conservan
> como referencia histórica, pero **no reflejan el flujo actual**.

---

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

---

## TU DÍA A DÍA (flujo vigente del repositorio)

Tu día a día pasa a ser esto:

```bash
git nueva paginacion-tareas      # ①
# ... programas, git add, git commit — las veces que quieras ...
git subir                        # ②
```

**Y ya está.** No esperas nada, no vuelves a `main`, no borras ramas.

## Qué hace cada uno

**①** te pone en `main`, la actualiza, borra las ramas locales que ya se
integraron y te crea la nueva. Empiezas siempre desde lo último y con la casa
recogida.

Entre medias trabajas **igual que siempre**: `git add`, `git commit`, tantos
commits como te apetezca. Haz commits pequeños y sucios si quieres, da igual —
por defecto se aplastan en uno solo al integrar.

**②** sube la rama, abre el PR y programa la integración. A partir de ahí
trabaja la máquina: arranca el CI, y cuando `CI en verde` pasa, se integra solo,
se borra la rama remota y se dispara el despliegue.

## `subir` acepta el método de integración

```bash
git subir            # squash (por defecto): tus commits se aplastan en uno
git subir rebase     # tus commits llegan a main tal cual, uno a uno
git subir merge      # commit de fusión
```

El squash es lo que quieres el 90 % de las veces: permite commitear sin pensar
durante el trabajo y deja `main` con una línea por cambio.

**Usa `rebase` cuando los commits cuenten una historia que merezca sobrevivir.**
Por ejemplo, una corrección de un fallo y los tests que lo cubren son dos cosas
distintas, y quien lea el historial dentro de un año agradecerá verlas
separadas. Si los divides a propósito, no dejes que el squash los vuelva a
juntar.

## Situaciones que te vas a encontrar

**El CI falla.** El PR se queda abierto, no se integra nada. Arreglas,
`git add`, `git commit`, y:

```bash
git push
```

A secas — el `-u` del primer push ya dejó la rama vinculada. El PR se actualiza,
el CI vuelve a correr y **la integración automática sigue armada**. No tienes
que repetir `git subir`.

**Quieres empezar otra cosa sin esperar.**

```bash
git nueva otra-cosa
```

El PR anterior sigue su curso por su cuenta. Trabajar en paralelo es gratis.

**Quieres ver cómo va.**

```bash
gh pr status      # tus PRs abiertos y su estado
gh pr checks      # los checks del PR de la rama actual
```

**Te arrepientes.**

```bash
gh pr merge --disable-auto    # desprograma la integración
gh pr close                   # cierra el PR sin integrar
```

## Por qué `nueva` limpia con `[gone]` y no con `--merged`

Lo intuitivo sería borrar las ramas así:

```bash
git branch --merged main | grep -v main | xargs git branch -d
```

**Y no funciona.** Con `--squash`, los commits de la rama no llegan a `main`:
llega uno nuevo, con el mismo contenido pero otro identificador. Git no
reconoce la fusión por ninguna parte, así que `--merged` no lista la rama y
`-d` se niega a borrarla. El comando se ejecuta, no da error, y no borra nada —
que es la peor forma de fallar.

La señal fiable es otra. Como `subir` integra con `--delete-branch`, al
fusionarse **desaparece la rama remota**. Después de podar, git marca la local
como huérfana:

```bash
git fetch --prune
git branch -vv | grep ': gone]' | awk '{print $1}'
```

Eso es lo que hace `nueva` antes de crear la rama nueva. Ojo con un detalle:
también alcanza a las ramas de un PR que cerraras sin integrar. Se recuperan
con `git reflog` durante unos noventa días.

## Los alias, por si hay que reinstalar

Van en `~/.gitconfig`, bajo `[alias]`. El valor **tiene que ir entre comillas
dobles**: sin ellas git trata cada `;` como el inicio de un comentario y parte
el alias por la mitad.

```ini
[alias]
	nueva = "!f() { [ -z \"$1\" ] && { echo \"Uso: git nueva <nombre-de-rama>\"; return 1; }; git checkout main && git pull --ff-only --prune || return 1; git branch -vv | grep ': gone]' | awk '{print $1}' | xargs -r git branch -D; git checkout -b \"$1\"; }; f"
	subir = "!f() { r=$(git rev-parse --abbrev-ref HEAD) || return 1; [ \"$r\" = \"main\" ] && { echo \"Estas en main. Empieza con: git nueva <rama>\"; return 1; }; metodo=\"${1:-squash}\"; case \"$metodo\" in squash|rebase|merge) ;; *) echo \"Metodo no valido: usa squash, rebase o merge.\"; return 1;; esac; gitdir=$(git rev-parse --git-dir); if [ -f \"$gitdir/MERGE_HEAD\" ]; then echo \"Hay un merge en curso sin terminar (MERGE_HEAD). Resuelvelo o abortalo antes de subir.\"; return 1; fi; if [ -n \"$(git status --porcelain)\" ]; then echo \"Tienes cambios sin commitear. Commitealos o descartalos antes de subir.\"; return 1; fi; pr_number=$(gh pr list --head \"$r\" --state open --json number --jq \".[0].number // empty\" 2>/dev/null); if [ -n \"$pr_number\" ]; then echo \"PR ya existente: #$pr_number\"; git push -u origin \"$r\" || return 1; else echo \"No hay un PR abierto para $r.\"; prior=$(gh pr list --head \"$r\" --state merged --json number --jq \".[0].number // empty\" 2>/dev/null); if [ -n \"$prior\" ]; then echo \"La rama $r ya se fusiono en el PR #$prior.\"; git fetch origin main -q 2>/dev/null; if git diff origin/main HEAD --quiet; then echo \"La rama $r no tiene cambios nuevos respecto a main. Nada que subir.\"; return 1; fi; echo \"Detectados cambios nuevos. Integro main...\"; if ! git merge origin/main --no-edit; then echo \"Conflictos al integrar main. Aborto el merge para no dejar la rama a medias.\"; git merge --abort; echo \"Resuelve a mano (git merge origin/main), commitea y repite: git subir\"; return 1; fi; fi; git push -u origin \"$r\" || return 1; echo \"Creando el PR...\"; pr_url=$(gh pr create --fill) || { echo \"Error: no se pudo crear el PR.\"; return 1; }; echo \"PR creado: $pr_url\"; pr_number=$(gh pr view \"$pr_url\" --json number --jq \".number\") || return 1; fi; gh pr merge \"$pr_number\" --\"$metodo\" --delete-branch --auto; }; f"
```

En `nueva`, el `||` en vez de encadenar con `&&` hasta el final no es un
descuido: si no hay ninguna rama huérfana, `grep` termina con error, y con `&&`
no llegarías a crear la rama.

En `subir`, las dos últimas versiones de este alias se corresponden con las
decisiones tomadas en las sesiones de la semana del 2026-09-19: el **blindaje**
(guardas de `MERGE_HEAD` y `git status --porcelain` antes de tocar nada) y la
**integración de `main`** cuando la rama ya se fusionó en un PR previo (`merged`)
— así el PR nuevo solo lleva el cambio nuevo, y un PR reabierto con historial
repetido se descarta con «nada que subir».

---

Comparado con lo de antes son **dos comandos más** —`nueva` al principio y `subir` en vez de `push`—, y a cambio ningún commit roto entra en `main` ni llega a producción.




---


## `git nueva <rama>` — camino completo

```
                git nueva prueba
                      │
                      ▼
              ❯ 1 │ cambiar a main
                      │
                      ▼
              ❯ 2 │ actualizar desde origin (con prune)
                      │                                (si falla → return 1)
                      ▼
              ❯ 3 │ listar ramas locales cuyo remoto
                  │  ya no existe  («: gone]»)
                      │
                      ▼
              ❯ 4 │ quedarse solo con el nombre
                  │  (awk '{print $1}')
                      │
                      ▼
              ❯ 5 │ borrarlas (git branch -D)
                      │
                      ▼
              ❯ 6 │ crear la rama nueva (git checkout -b)
                      │
                      ▼
                      prueba
```

**Explicación paso a paso:**

1. **Cambiar a `main`** — `git checkout main`; el alias trabaja siempre desde `main` para que la rama nueva parta de lo más fresco. Si no estás en `main` al ejecutarlo, te cambia solo.
2. **Actualizar desde origin** — `git pull --ff-only --prune`: trae lo último de `origin/main` (siempre fast-forward, sin merges sorpresa) y con `--prune` borra las refs de seguimiento de ramas remotas que ya no existen en el servidor (las que `git subir` eliminó al integrar). Si esto falla, `|| return 1` aborta el alias.
3. **Listar ramas locales «huérfanas»** — `git branch -vv | grep ': gone]'`: el `-vv` muestra el upstream de cada rama; `: gone]` marca las que apuntan a una rama remota ya borrada en origin. **Aquí es donde entra la poda automática** — solo actúa cuando el remoto desapareció; si la rama remota sigue viva (como pasó con las 3 legadas), no califica y no se toca.
4. **Quedarse con el nombre** — `awk '{print $1}'` extrae solo el nombre de cada rama detectada (la primera columna de la línea).
5. **Borrar las ramas huérfanas localmente** — `xargs -r git branch -D`: elimina todas las ramas listadas; `-r` hace que si no hay ninguna, no ejecute nada (evita un error vacío).
6. **Crear y cambiar a la rama nueva** — `git checkout -b "$1"` crea la rama con el nombre que pasaste (`prueba`, `BloqueC_RadioStack`, lo que sea) partiendo de `main` ya actualizado.

**Resultado:** empiezas en `prueba`, con `main` fresco y el árbol de ramas locales limpio de las ya integradas.

---

## `git subir` — camino completo

```
                 git subir [squash|rebase|merge]
                      │
                      ▼
              ❯ 1 │ leer rama actual (r)
                  │       (si falla → return 1)
                      │
                      ▼
              ❯ 2 │ ¿ramas = main? → «Estás en main» → ◘ stop
                      │
                      ▼
              ❯ 3 │ método default: squash
                  │   (si no es squash/rebase/merge → ◘ stop)
                      │
                      ▼
              ❯ 4 │ BLINDAJE: ¿MERGE_HEAD? → «merge en curso» → ◘ stop
                  │ ¿cambios sin commitear? → «commitéalos» → ◘ stop
                      │
                      ▼
              ❯ 5 │ ¿hay PR abierto de esta rama?
                  │     (gh pr list --head r --open)
                  ├──── SI ──────► ❯ 6 │ git push -u
                  │                          │
                  │                          ▼
                  │                 reutiliza ese PR (#)
                  │                          │──────────────┐
                  ▼ NO                       │              │
              ❯ 7 │ ¿hubo PR merged previo?   │              │
                  │     (gh pr list --merged)│              │
                  ├──── NO ──────────────────┤              │
                  │   │                       ▼              │
                  │   │               ❯ 8 │ ¿cambios vs main?
                  │   │                   │  (git diff origin/main HEAD --quiet)
                  │   │                   ├──── NO ──► «nada que subir» → ◘ stop
                  │   │                   │
                  │   │                   ▼
                  │   │               ❯ 9 │ integrar main
                  │   │                   │  (git merge origin/main --no-edit)
                  │   │                   ├── conflicto → abort + ◘ stop
                  │   │                   ▼
                  │   │              ❯ 10 │ git push -u
                  │   │                   ▼
                  │   │              ❯ 11 │ crear PR nuevo (gh pr create --fill)
                  │   │                   ▼
                  │   │              obtener su número
                  │   ▼                   │
                  ▼                       ▼
            ❯ 12 │ auto-merge: gh pr merge <#PR> --squash --delete-branch --auto
                      │
                      ▼
            PR fusiona cuando el CI pasa · rama remota borrada automáticamente
```

**Explicación paso a paso:**

1. **Leer la rama actual** — `r=$(git rev-parse --abbrev-ref HEAD)`: sabe en qué rama subes. Si no hay HEAD válido, aborta con error.
2. **Protección de `main`** — si estás en `main`, no pushea ni crea PRs desde ahí; te recuerda usar `git nueva <rama>`. `main` solo recibe merges, nunca se sube.
3. **Método de merge** — `metodo="${1:-squash}"`: por defecto `squash`; puedes pasar `git subir rebase` o `git subir merge`. Solo acepta esos tres; cualquier otra cosa aborta.
4. **Blindaje** (las guardas que acabamos de instalar):
   - Si existe `MERGE_HEAD` → hay un merge a medias sin resolver → se detiene antes de tocar nada.
   - Si `git status --porcelain` no está vacío → hay cambios sin commitear → se detiene. Evita subir un PR «a medias».
5. **¿PR ya abierto?** — consulta si la rama ya tiene un PR abierto. Si existe, no duplica: pushea los cambios nuevos y reutiliza ese PR (salta al paso 12).
6. **Push de actualización** — `git push -u origin r` empuja los commits nuevos a la rama del PR ya abierto.
7. **¿Rama con PR fusionado antes?** — el caso «PR cerrado adelante» que resolvimos: si esta rama ya se integró en el pasado, el alias lo detecta para no reabrir un PR que repita historia.
8. **Comprobación de cambios** — `git diff origin/main HEAD --quiet`: si la rama no tiene nada nuevo respecto a `main`, no crea un PR vacío: avisa «nada que subir» y para.
9. **Integrar main** — si hay cambios nuevos, hace `git merge origin/main --no-edit` para que el PR nuevo solo contenga tu cambio. Si hay conflictos, aborta el merge (`git merge --abort`) con la rama intacta y te pide resolver a mano.
10. **Push inicial** — lanza la rama a origin.
11. **Crear PR** — `gh pr create --fill` toma título y cuerpo del commit, y obtiene el número del PR nuevo.
12. **Auto-merge** — `gh pr merge <#PR> --<método> --delete-branch --auto`: agenda el merge automático en cuanto el CI pase; con `--delete-branch` borra la rama remota al integrarse (que luego `git nueva` limpia en local).

**Resultado:** tu cambio entra en `main` sin intervención manual (si el CI va verde), la rama remota se borra sola, y en la siguiente tarea el árbol queda podado.