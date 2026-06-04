import ast
from pathlib import Path

import pytest

API_DIR = Path(__file__).resolve().parents[2] / "app" / "api"
FORBIDDEN_CONCRETE_IMPORTS = {
    "VertexAIClient",
    "OpenAIClient",
    "ChromaVectorStore",
    "VertexVectorSearchStore",
    "MockLLMClient",
}


def _imported_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                names.add(alias.name)
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


@pytest.mark.parametrize("path", sorted(API_DIR.glob("*.py")))
def test_api_modules_do_not_import_provider_concrete_classes(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imported = _imported_names(tree)
    hits = imported & FORBIDDEN_CONCRETE_IMPORTS
    assert not hits, f"{path.name} must not import concrete providers: {hits}"


def test_app_imports_without_optional_vector_deps() -> None:
    """Smoke import of FastAPI app in mock+none mode."""
    import os

    os.environ["LLM_PROVIDER"] = "mock"
    os.environ["VECTOR_STORE_PROVIDER"] = "none"
    from app.main import app  # noqa: F401

    assert app is not None
