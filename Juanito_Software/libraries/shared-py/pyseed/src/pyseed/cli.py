"""
CLI entrypoint and interactive interface for pyseed.
"""

import argparse
import sys
import os
import subprocess
import threading
import time
from pathlib import Path
from pyseed import __version__
from pyseed.generator import generate_project, get_dir_tree_string, sanitize_package_name

# ANSI escape codes for stunning console aesthetics
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_WHITE = "\033[97m"
C_GRAY = "\033[90m"
C_BOLD = "\033[1m"
C_UNDERLINE = "\033[4m"
C_RESET = "\033[0m"

# Beautiful decorations
SUCCESS_ICON = f"{C_GREEN}✔{C_RESET}"
INFO_ICON = f"{C_BLUE}ℹ{C_RESET}"
WARN_ICON = f"{C_YELLOW}⚠{C_RESET}"
ERROR_ICON = f"{C_RED}✖{C_RESET}"

def print_banner():
    banner = f"""
{C_CYAN}{C_BOLD}┌────────────────────────────────────────────────────────┐
│  🌱  pyseed {C_WHITE}v{__version__}{C_CYAN} - Python Project Generator             │
│  {C_GRAY}Genera estructuras limpias e impecables de inmediato{C_CYAN}  │
└────────────────────────────────────────────────────────┘{C_RESET}"""
    print(banner)

def get_git_config(key: str) -> str:
    """Helper to fetch git config values for smart defaults."""
    try:
        result = subprocess.run(
            ["git", "config", key],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""

def prompt_input(question: str, default: str = "") -> str:
    """Prompts the user for a text input with a stylized question."""
    default_text = f" {C_GRAY}(default: {default}){C_RESET}" if default else ""
    prompt = f"{C_BOLD}{C_BLUE}?{C_RESET} {question}{default_text}: "
    
    try:
        val = input(prompt).strip()
        return val if val else default
    except (KeyboardInterrupt, EOFError):
        print(f"\n{ERROR_ICON} Operación cancelada por el usuario.")
        sys.exit(1)

def prompt_confirm(question: str, default: bool = True) -> bool:
    """Prompts the user for a yes/no question with a stylized format."""
    choices = " [Y/n]" if default else " [y/N]"
    prompt = f"{C_BOLD}{C_BLUE}?{C_RESET} {question}{C_GRAY}{choices}{C_RESET}: "
    
    try:
        val = input(prompt).strip().lower()
        if not val:
            return default
        return val in ("y", "yes", "si", "sí", "t", "true")
    except (KeyboardInterrupt, EOFError):
        print(f"\n{ERROR_ICON} Operación cancelada por el usuario.")
        sys.exit(1)

def prompt_select(question: str, options: list[str], default_index: int = 0) -> str:
    """Prompts the user to select one option from a clean numbered menu."""
    print(f"{C_BOLD}{C_BLUE}?{C_RESET} {question}")
    for idx, opt in enumerate(options):
        marker = "❯" if idx == default_index else " "
        color = C_CYAN if idx == default_index else C_RESET
        print(f"  {C_GRAY}{idx + 1}){C_RESET} {color}{opt}{C_RESET}")
    
    default_val = str(default_index + 1)
    prompt = f"  {C_BOLD}Selecciona una opción [1-{len(options)}]{C_GRAY} (default: {default_val}){C_RESET}: "
    
    try:
        while True:
            val = input(prompt).strip()
            if not val:
                return options[default_index]
            if val.isdigit():
                choice_idx = int(val) - 1
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
            print(f"    {C_RED}Opción inválida. Inténtalo de nuevo.{C_RESET}")
    except (KeyboardInterrupt, EOFError):
        print(f"\n{ERROR_ICON} Operación cancelada por el usuario.")
        sys.exit(1)

def run_with_spinner(target_func, options: dict) -> tuple[bool, list[str]]:
    """Runs the generator in a background thread while displaying an attractive terminal spinner."""
    result = [False]
    logs = []
    done = threading.Event()
    
    def worker():
        try:
            result[0], res_logs = target_func(options)
            logs.extend(res_logs)
        except Exception as e:
            logs.append(f"Excepción: {str(e)}")
        finally:
            done.set()

    thread = threading.Thread(target=worker)
    thread.start()
    
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not done.wait(0.08):
        char = spinner_chars[i % len(spinner_chars)]
        sys.stdout.write(f"\r{C_YELLOW}{char}{C_RESET} {C_BOLD}Sembrando proyecto...{C_RESET}")
        sys.stdout.flush()
        i += 1
        
    sys.stdout.write("\r" + " " * 40 + "\r")  # Clear spinner line
    sys.stdout.flush()
    return result[0], logs

def run_interactive() -> dict:
    """Launches the interactive step-by-step project seeding assistant."""
    print_banner()
    
    options = {}
    
    # 1. Project Name
    while True:
        name = prompt_input("Nombre del proyecto (e.g. mi-proyecto-python)")
        if name:
            options["project_name"] = name
            break
        print(f"  {C_RED}El nombre del proyecto es obligatorio.{C_RESET}")
        
    # 2. Description
    options["description"] = prompt_input("Descripción breve", "A modern Python project")
    
    # 3. Version
    options["version"] = prompt_input("Versión inicial", "0.1.0")
    
    # 4. Author Name & Email (Auto-filled from Git if possible)
    git_author = get_git_config("user.name") or "Developer"
    options["author_name"] = prompt_input("Nombre del autor", git_author)
    
    git_email = get_git_config("user.email") or "developer@example.com"
    options["author_email"] = prompt_input("Correo electrónico del autor", git_email)
    
    # 5. Python version constraint
    options["python_version"] = prompt_input("Versión de Python compatible", ">=3.8")
    
    # 6. License
    license_choices = ["MIT", "Apache 2.0", "GPLv3", "BSD 3-Clause", "Ninguna"]
    selected_license = prompt_select("Licencia del proyecto", license_choices, 2)
    options["license_name"] = selected_license if selected_license != "Ninguna" else "None"
    
    # 7. CLI Template
    options["include_cli"] = prompt_confirm("¿Incluir plantilla de comandos (CLI ejecutable)?", False)
    
    # 8. Testing framework
    options["include_tests"] = prompt_confirm("¿Crear estructura de pruebas unitarias?", True)
    if options["include_tests"]:
        frameworks = ["pytest", "unittest"]
        options["test_framework"] = prompt_select("Framework de pruebas", frameworks, 0)
        
    # 9. Environments (Git, Poetry / Venv)
    options["init_git"] = prompt_confirm("¿Inicializar repositorio Git automáticamente?", True)
    options["use_poetry"] = prompt_confirm("¿Usar Poetry como gestor de dependencias?", False)
    if options["use_poetry"]:
        options["create_venv"] = False
    else:
        options["create_venv"] = prompt_confirm("¿Crear entorno virtual (.venv)?", False)
    
    options["output_dir"] = Path(".")
    
    return options

def parse_arguments() -> tuple[argparse.Namespace, dict]:
    """Sets up argparse for command line argument mode."""
    parser = argparse.ArgumentParser(
        description="pyseed: Generador automático de proyectos Python limpios y modernos."
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        default=None,
        help="Nombre del proyecto a generar. Si se omite, iniciará en modo interactivo."
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Directorio destino (por defecto: directorio actual)."
    )
    parser.add_argument(
        "-d", "--description",
        default="A modern Python project",
        help="Descripción del proyecto."
    )
    parser.add_argument(
        "-v", "--version",
        default="0.1.0",
        help="Versión inicial del proyecto (por defecto: 0.1.0)."
    )
    parser.add_argument(
        "-a", "--author",
        default=None,
        help="Nombre del autor (por defecto: usuario de Git)."
    )
    parser.add_argument(
        "-e", "--email",
        default=None,
        help="Email del autor (por defecto: email de Git)."
    )
    parser.add_argument(
        "-l", "--license",
        default="GPLv3",
        choices=["MIT", "Apache 2.0", "GPLv3", "BSD 3-Clause", "None"],
        help="Licencia del proyecto (por defecto: GPLv3)."
    )
    parser.add_argument(
        "--python",
        default=">=3.8",
        help="Restricción de versión de Python (por defecto: >=3.8)."
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Generar entrypoint CLI ejecutable."
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Omitir la creación del directorio de pruebas unitarias."
    )
    parser.add_argument(
        "--framework",
        default="pytest",
        choices=["pytest", "unittest"],
        help="Framework de pruebas a usar (por defecto: pytest)."
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="No inicializar repositorio Git."
    )
    parser.add_argument(
        "--venv",
        action="store_true",
        help="Crear entorno virtual .venv automáticamente."
    )
    parser.add_argument(
        "--poetry",
        action="store_true",
        help="Usar Poetry como gestor de dependencias (genera pyproject.toml para Poetry y scripts .bat). Incompatible con --venv."
    )
    parser.add_argument(
        "--defaults",
        action="store_true",
        help="Usar valores por defecto para todos los campos no especificados."
    )
    parser.add_argument(
        "--version-cli",
        action="version",
        version=f"pyseed {__version__}",
        help="Muestra la versión de pyseed."
    )
    
    args = parser.parse_args()
    
    # Map CLI arguments to generator options dictionary
    options = {
        "project_name": args.project_name,
        "output_dir": Path(args.output_dir),
        "description": args.description,
        "version": args.version,
        "author_name": args.author or get_git_config("user.name") or "Developer",
        "author_email": args.email or get_git_config("user.email") or "developer@example.com",
        "license_name": args.license,
        "python_version": args.python,
        "include_cli": args.cli,
        "include_tests": not args.no_tests,
        "test_framework": args.framework,
        "init_git": not args.no_git,
        "use_poetry": args.poetry,
        "create_venv": args.venv and not args.poetry
    }
    
    return args, options

def main():
    args, options = parse_arguments()
    
    # If no project name was provided on the CLI, switch to fully interactive mode
    if options["project_name"] is None:
        try:
            options = run_interactive()
        except KeyboardInterrupt:
            print(f"\n{ERROR_ICON} Operación cancelada.")
            sys.exit(1)
    else:
        # If we have arguments but not --defaults, let's inform the user we are running in fast non-interactive mode
        print(f"{INFO_ICON} Sembrando nuevo proyecto '{options['project_name']}'...")

    # Run the generator with the premium spinner
    success, logs = run_with_spinner(generate_project, options)
    
    print()  # New line
    if success:
        # Show success banner
        print(f"{SUCCESS_ICON} {C_GREEN}{C_BOLD}¡Proyecto creado con éxito! 🎉{C_RESET}\n")
        
        # Display the beautiful unicode directory tree
        output_dir = Path(options.get("output_dir", ".")).resolve() / options["project_name"]
        print(f"{C_CYAN}{C_BOLD}Estructura del Proyecto Generado:{C_RESET}")
        tree_string = get_dir_tree_string(output_dir)
        print(tree_string)
        
        # Next steps card
        package_name = sanitize_package_name(options["project_name"])
        print(f"{C_YELLOW}{C_BOLD}Siguientes Pasos Recomendados:{C_RESET}")
        print(f"  {C_CYAN}1.{C_RESET} Entrar al directorio:")
        print(f"     {C_BOLD}cd {options['project_name']}{C_RESET}")
        
        if options.get("use_poetry"):
            print(f"  {C_CYAN}2.{C_RESET} Instalar dependencias con Poetry:")
            print(f"     {C_BOLD}poetry install{C_RESET}")
            run_cmd = f"poetry run {options['project_name']}" if options.get("include_cli") else f"poetry run python -m {package_name}"
            print(f"  {C_CYAN}3.{C_RESET} Ejecutar el proyecto:")
            print(f"     {C_BOLD}{run_cmd}{C_RESET}")
            print(f"     {C_GRAY}O usar los scripts: scripts\\setup.bat / scripts\\run.bat{C_RESET}")
        elif options.get("create_venv"):
            print(f"  {C_CYAN}2.{C_RESET} Activar el entorno virtual:")
            if sys.platform == "win32":
                print(f"     {C_BOLD}.\\.venv\\Scripts\\activate{C_RESET}")
            else:
                print(f"     {C_BOLD}source .venv/bin/activate{C_RESET}")
            print(f"  {C_CYAN}3.{C_RESET} Instalar en modo desarrollo local:")
            print(f"     {C_BOLD}pip install -e .{C_RESET}")
        else:
            print(f"  {C_CYAN}2.{C_RESET} Crear e instalar en entorno de desarrollo:")
            if sys.platform == "win32":
                print(f"     {C_BOLD}python -m venv .venv && .\\.venv\\Scripts\\activate && pip install -e .{C_RESET}")
            else:
                print(f"     {C_BOLD}python -m venv .venv && source .venv/bin/activate && pip install -e .{C_RESET}")
        
        test_cmd = "pytest" if (options.get("include_tests") and options.get("test_framework") == "pytest") else "python -m unittest"
        print(f"  {C_CYAN}4.{C_RESET} Ejecutar pruebas:")
        print(f"     {C_BOLD}{test_cmd}{C_RESET}")
        
        if options.get("include_cli"):
            print(f"  {C_CYAN}5.{C_RESET} Probar la utilidad CLI integrada:")
            print(f"     {C_BOLD}{options['project_name']}{C_RESET} o {C_BOLD}python -m {package_name}{C_RESET}")
            
        print(f"\n{C_GRAY}¡Feliz codificación! 🚀{C_RESET}")
    else:
        # Show detailed error logs
        print(f"{ERROR_ICON} {C_RED}{C_BOLD}Error al crear el proyecto:{C_RESET}")
        for log_line in logs:
            print(f"  {C_GRAY}›{C_RESET} {log_line}")
        sys.exit(1)

if __name__ == "__main__":
    main()
