"""Root pytest configuration — loads modular fixture plugins."""

pytest_plugins = [
    "tests.fixtures.environment",
    "tests.fixtures.database",
    "tests.fixtures.api",
]
