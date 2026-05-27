"""
Generator module for pyseed.
Handles the creation of files, directories, Git initialization, and Virtual Environment setup.
"""

import os
import re
import shutil
import subprocess
import datetime
from pathlib import Path
from pyseed.templates import (
    PYPROJECT_TEMPLATE,
    PYTEST_SECTION_TEMPLATE,
    README_TEMPLATE,
    GITIGNORE_TEMPLATE,
    GITATTRIBUTES_TEMPLATE,
    INIT_TEMPLATE,
    CORE_TEMPLATE,
    MAIN_TEMPLATE,
    CLI_TEMPLATE,
    TEST_CORE_PYTEST_TEMPLATE,
    TEST_CORE_UNITTEST_TEMPLATE,
    LICENSES
)

def sanitize_package_name(name: str) -> str:
    """
    Sanitizes a project name to be a valid Python package identifier.
    Replaces spaces, dots, and hyphens with underscores and converts to lowercase.
    """
    sanitized = name.strip().lower()
    # Strip any leading non-alphabetic characters first to avoid leading underscores/dots
    sanitized = re.sub(r'^[^a-z]+', '', sanitized)
    sanitized = re.sub(r'[-. \s]+', '_', sanitized)
    sanitized = re.sub(r'[^a-z0-9_]', '', sanitized)
    if not sanitized:
        sanitized = "my_package"
    return sanitized

def run_command(cmd: list, cwd: Path) -> tuple[bool, str]:
    """
    Helper to run a subprocess command safely.
    Returns (success, output/error_message).
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return True, result.stdout
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        error_msg = getattr(e, 'stderr', '') or str(e)
        return False, error_msg

def generate_project(options: dict, progress_callback=None) -> tuple[bool, list[str]]:
    """
    Generates the Python project structure based on the options dictionary.
    Yields progress or calls progress_callback if provided.
    Returns (success_status, logs).
    """
    logs = []
    
    def log(msg: str):
        logs.append(msg)
        if progress_callback:
            progress_callback(msg)

    try:
        project_name = options.get("project_name", "my-project").strip()
        package_name = sanitize_package_name(project_name)
        output_dir = Path(options.get("output_dir", ".")).resolve() / project_name
        
        version = options.get("version", "0.1.0")
        description = options.get("description", "A modern Python project")
        author_name = options.get("author_name", "Developer")
        author_email = options.get("author_email", "developer@example.com")
        license_name = options.get("license_name", "MIT")
        python_version = options.get("python_version", ">=3.8")
        
        include_cli = options.get("include_cli", False)
        include_tests = options.get("include_tests", True)
        test_framework = options.get("test_framework", "pytest")
        
        init_git = options.get("init_git", True)
        create_venv = options.get("create_venv", False)

        log(f"Creando directorio del proyecto en: {output_dir}")
        if output_dir.exists():
            if any(output_dir.iterdir()):
                return False, [f"Error: El directorio {output_dir} ya existe y no está vacío."]
        else:
            output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Create directory structure
        src_dir = output_dir / "src"
        pkg_dir = src_dir / package_name
        log(f"Creando estructura del paquete: src/{package_name}")
        pkg_dir.mkdir(parents=True, exist_ok=True)

        if include_tests:
            tests_dir = output_dir / "tests"
            log("Creando directorio de pruebas: tests/")
            tests_dir.mkdir(parents=True, exist_ok=True)

        # 2. Write package source files
        log("Escribiendo archivos fuente...")
        (pkg_dir / "__init__.py").write_text(
            INIT_TEMPLATE.format(version=version),
            encoding="utf-8"
        )
        
        (pkg_dir / "core.py").write_text(
            CORE_TEMPLATE.format(project_name=project_name),
            encoding="utf-8"
        )

        if include_cli:
            log("Escribiendo entrypoints del CLI...")
            (pkg_dir / "cli.py").write_text(
                CLI_TEMPLATE.format(project_name=project_name, description=description, package_name=package_name),
                encoding="utf-8"
            )
            (pkg_dir / "__main__.py").write_text(
                MAIN_TEMPLATE.format(package_name=package_name, project_name=project_name),
                encoding="utf-8"
            )

        # 3. Write test files
        if include_tests:
            log("Configurando pruebas...")
            (tests_dir / "__init__.py").write_text("", encoding="utf-8")
            if test_framework == "pytest":
                (tests_dir / f"test_{package_name}.py").write_text(
                    TEST_CORE_PYTEST_TEMPLATE.format(package_name=package_name, project_name=project_name),
                    encoding="utf-8"
                )
            else:
                (tests_dir / f"test_{package_name}.py").write_text(
                    TEST_CORE_UNITTEST_TEMPLATE.format(package_name=package_name, project_name=project_name),
                    encoding="utf-8"
                )

        # 4. Write static / config files
        log("Escribiendo archivos de configuración (.gitignore, .gitattributes)...")
        (output_dir / ".gitignore").write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
        (output_dir / ".gitattributes").write_text(GITATTRIBUTES_TEMPLATE, encoding="utf-8")

        # 5. Write LICENSE
        if license_name in LICENSES:
            log(f"Generando archivo LICENSE ({license_name})...")
            year = datetime.datetime.now().year
            license_text = LICENSES[license_name].format(year=year, author=author_name)
            (output_dir / "LICENSE").write_text(license_text, encoding="utf-8")
        else:
            log("Sin licencia especificada.")

        # 6. Write pyproject.toml
        log("Configurando pyproject.toml...")
        cli_scripts_section = ""
        if include_cli:
            cli_scripts_section = (
                f"[project.scripts]\n"
                f"{project_name} = \"{package_name}.cli:main\"\n"
            )

        pytest_section = ""
        if include_tests and test_framework == "pytest":
            pytest_section = PYTEST_SECTION_TEMPLATE

        pyproject_content = PYPROJECT_TEMPLATE.format(
            project_name=project_name,
            package_name=package_name,
            version=version,
            description=description,
            python_version=python_version,
            license_name=license_name,
            author_name=author_name,
            author_email=author_email,
            cli_scripts_section=cli_scripts_section,
            pytest_section=pytest_section
        )
        (output_dir / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")

        # 7. Write README.md
        log("Escribiendo README.md...")
        usage_instructions = ""
        if include_cli:
            usage_instructions = (
                f"Ejecutar la utilidad CLI directamente / Run CLI utility directly:\n"
                f"```bash\n"
                f"{project_name}\n"
                f"```\n"
                f"O mediante módulo Python / Or via Python module:\n"
                f"```bash\n"
                f"python -m {package_name}\n"
                f"```"
            )
        else:
            usage_instructions = (
                f"Importar y usar en tu código / Import and use in your code:\n"
                f"```python\n"
                f"import {package_name}\n"
                f"print({package_name}.core.greet())\n"
                f"```"
            )

        test_run_command = "pytest" if (include_tests and test_framework == "pytest") else "python -m unittest discover -s tests"
        readme_content = README_TEMPLATE.format(
            project_name=project_name,
            description=description,
            usage_instructions=usage_instructions,
            test_run_command=test_run_command,
            license_name=license_name
        )
        (output_dir / "README.md").write_text(readme_content, encoding="utf-8")

        # 8. Git initialization
        if init_git:
            log("Inicializando repositorio Git...")
            git_ok, git_out = run_command(["git", "init"], output_dir)
            if git_ok:
                run_command(["git", "add", "."], output_dir)
                log("Repositorio Git inicializado y archivos añadidos al staging.")
            else:
                log(f"Aviso: No se pudo inicializar Git. ¿Está instalado? Detalles: {git_out}")

        # 9. Create Virtual Environment
        if create_venv:
            log("Creando entorno virtual Python (.venv)... (esto puede tardar unos segundos)")
            venv_ok, venv_out = run_command(["python", "-m", "venv", ".venv"], output_dir)
            if venv_ok:
                log("Entorno virtual (.venv) creado exitosamente.")
            else:
                log(f"Aviso: No se pudo crear el entorno virtual. Detalles: {venv_out}")

        log("¡Generación del proyecto finalizada con éxito!")
        return True, logs

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return False, logs + [f"Excepción ocurrida: {str(e)}", error_trace]


def get_dir_tree_string(path: Path, prefix: str = "", is_last: bool = True) -> str:
    """
    Returns a beautiful Unicode tree representation of the generated files.
    Filters out common dynamic runtime folders like .venv, .git, and __pycache__ for a clean output.
    """
    ignored_dirs = {".git", ".venv", "__pycache__", ".pytest_cache", "dist", "build"}
    
    if not path.exists():
        return ""

    output = ""
    basename = path.name
    
    # Draw current node
    if prefix:
        connector = "└── " if is_last else "├── "
        icon = "📁 " if path.is_dir() else "📄 "
        output += f"{prefix}{connector}{icon}{basename}\n"
    else:
        output += f"📁 {basename}\n"

    if path.is_dir():
        # Update prefix for children
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Get children and filter
        children = sorted(
            [c for c in path.iterdir() if c.name not in ignored_dirs],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
        
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1)
            output += get_dir_tree_string(child, new_prefix, is_child_last)
            
    return output
