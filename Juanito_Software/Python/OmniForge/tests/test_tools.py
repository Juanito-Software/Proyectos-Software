"""Tests del contrato de herramientas — la cifra documentada en el README (29 tools, 5 módulos)."""
from tools import ALL_TOOLS
from tools.filesystem import FILESYSTEM_TOOLS
from tools.terminal import TERMINAL_TOOLS
from tools.browser import BROWSER_TOOLS
from tools.screen import SCREEN_TOOLS
from tools.vision import VISION_TOOLS


def test_hay_29_herramientas_en_total():
    assert len(ALL_TOOLS) == 29


def test_modulo_filesystem_tiene_4():
    assert len(FILESYSTEM_TOOLS) == 4


def test_modulo_terminal_tiene_2():
    assert len(TERMINAL_TOOLS) == 2


def test_modulo_browser_tiene_3():
    assert len(BROWSER_TOOLS) == 3


def test_modulo_screen_tiene_16():
    assert len(SCREEN_TOOLS) == 16


def test_modulo_vision_tiene_4():
    assert len(VISION_TOOLS) == 4


def test_nombres_esperados_estan_presentes():
    nombres = {t.name for t in ALL_TOOLS}
    esperados = {
        "read_file", "write_file", "list_dir", "delete_file",
        "run_code", "run_command",
        "browse_url", "web_search", "extract_page_content",
        "take_screenshot", "click", "type_text", "press_key",
        "read_screen_text", "find_text_on_screen",
        "describe_screen", "find_element",
    }
    assert esperados <= nombres


def test_nombres_son_unicos():
    nombres = [t.name for t in ALL_TOOLS]
    assert len(nombres) == len(set(nombres))