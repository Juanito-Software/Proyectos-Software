"""
Unit tests for the pyseed generator.
Runs entirely using the standard library's unittest.
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path

# Add src/ to path so we can import without installing
import sys
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from pyseed.generator import (
    sanitize_package_name,
    generate_project,
    get_dir_tree_string
)

class TestGenerator(unittest.TestCase):

    def test_sanitize_package_name(self):
        self.assertEqual(sanitize_package_name("my-awesome-project"), "my_awesome_project")
        self.assertEqual(sanitize_package_name("My Project 123"), "my_project_123")
        self.assertEqual(sanitize_package_name("...invalid-start"), "invalid_start")
        self.assertEqual(sanitize_package_name("already_correct"), "already_correct")
        self.assertEqual(sanitize_package_name("- - -"), "my_package")

    def test_generate_project_minimal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            options = {
                "project_name": "test-project",
                "output_dir": temp_path,
                "version": "1.2.3",
                "description": "Test description",
                "author_name": "Test Author",
                "author_email": "test@example.com",
                "license_name": "MIT",
                "python_version": ">=3.9",
                "include_cli": False,
                "include_tests": False,
                "init_git": False,
                "create_venv": False
            }

            success, logs = generate_project(options)
            self.assertTrue(success, f"Generation failed: {logs}")
            
            project_dir = temp_path / "test-project"
            self.assertTrue(project_dir.exists())
            self.assertTrue((project_dir / "pyproject.toml").exists())
            self.assertTrue((project_dir / "README.md").exists())
            self.assertTrue((project_dir / "LICENSE").exists())
            self.assertTrue((project_dir / ".gitignore").exists())
            self.assertTrue((project_dir / ".gitattributes").exists())
            
            # Check source directory and package
            pkg_dir = project_dir / "src" / "test_project"
            self.assertTrue(pkg_dir.exists())
            self.assertTrue((pkg_dir / "__init__.py").exists())
            self.assertTrue((pkg_dir / "core.py").exists())
            
            # CLI files should NOT exist
            self.assertFalse((pkg_dir / "cli.py").exists())
            self.assertFalse((pkg_dir / "__main__.py").exists())

            # Read pyproject.toml to verify contents
            pyproject_content = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
            self.assertIn('name = "test-project"', pyproject_content)
            self.assertIn('version = "1.2.3"', pyproject_content)
            self.assertIn('description = "Test description"', pyproject_content)
            self.assertIn('license = { text = "MIT" }', pyproject_content)
            self.assertIn('packages = ["src/test_project"]', pyproject_content)

    def test_generate_project_with_cli(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            options = {
                "project_name": "cli-project",
                "output_dir": temp_path,
                "version": "0.1.0",
                "description": "CLI description",
                "author_name": "Author",
                "author_email": "auth@example.com",
                "license_name": "MIT",
                "python_version": ">=3.8",
                "include_cli": True,
                "include_tests": False,
                "init_git": False,
                "create_venv": False
            }

            success, logs = generate_project(options)
            self.assertTrue(success, f"Generation failed: {logs}")
            
            project_dir = temp_path / "cli-project"
            pkg_dir = project_dir / "src" / "cli_project"
            
            self.assertTrue((pkg_dir / "cli.py").exists())
            self.assertTrue((pkg_dir / "__main__.py").exists())

            # Verify entrypoint in pyproject.toml
            pyproject_content = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
            self.assertIn("[project.scripts]", pyproject_content)
            self.assertIn('cli-project = "cli_project.cli:main"', pyproject_content)

    def test_generate_project_with_tests_pytest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            options = {
                "project_name": "test-project-pytest",
                "output_dir": temp_path,
                "include_tests": True,
                "test_framework": "pytest",
                "init_git": False,
                "create_venv": False
            }

            success, logs = generate_project(options)
            self.assertTrue(success)
            
            project_dir = temp_path / "test-project-pytest"
            tests_dir = project_dir / "tests"
            self.assertTrue(tests_dir.exists())
            self.assertTrue((tests_dir / "__init__.py").exists())
            self.assertTrue((tests_dir / "test_test_project_pytest.py").exists())
            
            # Verify pytest settings in pyproject.toml
            pyproject_content = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
            self.assertIn("[tool.pytest.ini_options]", pyproject_content)

    def test_generate_project_with_tests_unittest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            options = {
                "project_name": "test-project-unittest",
                "output_dir": temp_path,
                "include_tests": True,
                "test_framework": "unittest",
                "init_git": False,
                "create_venv": False
            }

            success, logs = generate_project(options)
            self.assertTrue(success)
            
            project_dir = temp_path / "test-project-unittest"
            tests_dir = project_dir / "tests"
            self.assertTrue(tests_dir.exists())
            self.assertTrue((tests_dir / "__init__.py").exists())
            self.assertTrue((tests_dir / "test_test_project_unittest.py").exists())
            
            # Verify unittest style in test file (uses import unittest)
            test_content = (tests_dir / "test_test_project_unittest.py").read_text(encoding="utf-8")
            self.assertIn("import unittest", test_content)
            self.assertIn("class TestCore(unittest.TestCase):", test_content)

    def test_get_dir_tree_string(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a simple dummy directory tree
            d1 = temp_path / "dummy"
            d1.mkdir()
            (d1 / "file1.txt").write_text("hello")
            
            d2 = d1 / "subdir"
            d2.mkdir()
            (d2 / "file2.py").write_text("print('hello')")
            
            # Excluded folders
            d3 = d1 / ".git"
            d3.mkdir()
            (d3 / "config").write_text("git config")
            
            tree_str = get_dir_tree_string(d1)
            
            self.assertIn("dummy", tree_str)
            self.assertIn("file1.txt", tree_str)
            self.assertIn("subdir", tree_str)
            self.assertIn("file2.py", tree_str)
            self.assertNotIn(".git", tree_str)  # Should filter .git out!
            self.assertNotIn("config", tree_str)

if __name__ == "__main__":
    unittest.main()
