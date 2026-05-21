"""
Templates for the pyseed project generator.
Contains raw template contents for files like pyproject.toml, README, licenses, gitignore, and core code.
"""

PYPROJECT_TEMPLATE = """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "{version}"
description = "{description}"
readme = "README.md"
requires-python = "{python_version}"
license = {{ text = "{license_name}" }}
authors = [
    {{ name = "{author_name}", email = "{author_email}" }}
]
dependencies = []
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]

{cli_scripts_section}
[tool.hatch.build.targets.wheel]
packages = ["src/{package_name}"]

{pytest_section}"""

PYTEST_SECTION_TEMPLATE = """[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "tests",
]
"""

README_TEMPLATE = """# {project_name}

{description}

A modern Python project generated automatically with `pyseed`.

## 📦 Instalación / Installation

Instalar en modo desarrollo local / Install in local development mode:
```bash
pip install -e .
```

## 🚀 Uso / Usage

{usage_instructions}

## 🧪 Pruebas / Testing

Ejecutar las pruebas unitarias / Run unit tests:
```bash
{test_run_command}
```

## 📝 Licencia / License

Este proyecto está bajo la licencia `{license_name}`. Ver el archivo [LICENSE](LICENSE) para más detalles.
"""

GITIGNORE_TEMPLATE = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
bin/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script, but may be useful to exclude
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.compet/
.pytest_cache/
.pytest_cache/
.hypothesis/
.ruamel_datetime/

# Translations
*.mo
*.gmo

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# PEP 582; project local imports without virtualenv
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# OS specific files
.DS_Store
Thumbs.db
"""

GITATTRIBUTES_TEMPLATE = """# Auto detect text files and perform LF normalization
* text=auto eol=lf
"""

INIT_TEMPLATE = """__version__ = "{version}"
"""

CORE_TEMPLATE = """\"\"\"
Core functionality for {project_name}.
\"\"\"

def greet(name: str = "World") -> str:
    \"\"\"
    Returns a friendly greeting.
    \"\"\"
    return f"Hello, {{name}}! Welcome to {project_name}."
"""

MAIN_TEMPLATE = """\"\"\"
Entrypoint module for {project_name}.
Allows running the package directly via `python -m {package_name}`.
\"\"\"

from {package_name}.cli import main

if __name__ == "__main__":
    main()
"""

CLI_TEMPLATE = """\"\"\"
CLI interface for {project_name}.
\"\"\"

import argparse
from {package_name} import __version__
from {package_name}.core import greet

def parse_args():
    parser = argparse.ArgumentParser(
        description="{description}"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {{__version__}}"
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="Developer",
        help="Name to greet"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    greeting = greet(args.name)
    print(greeting)

if __name__ == "__main__":
    main()
"""

TEST_CORE_PYTEST_TEMPLATE = """from {package_name}.core import greet

def test_greet():
    assert greet("Pyseed User") == "Hello, Pyseed User! Welcome to {project_name}."
    assert greet() == "Hello, World! Welcome to {project_name}."
"""

TEST_CORE_UNITTEST_TEMPLATE = """import unittest
from {package_name}.core import greet

class TestCore(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Pyseed User"), "Hello, Pyseed User! Welcome to {project_name}.")
        self.assertEqual(greet(), "Hello, World! Welcome to {project_name}.")

if __name__ == "__main__":
    unittest.main()
"""

# License Templates
LICENSE_MIT = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

LICENSE_APACHE = """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright {year} {author}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

LICENSE_GPL = """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {year} {author}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

LICENSE_BSD3 = """BSD 3-Clause License

Copyright (c) {year}, {author}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

LICENSES = {
    "MIT": LICENSE_MIT,
    "Apache 2.0": LICENSE_APACHE,
    "GPLv3": LICENSE_GPL,
    "BSD 3-Clause": LICENSE_BSD3
}
