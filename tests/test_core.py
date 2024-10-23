from gitlab_project_exporter.core import app


def test_app() -> None:
    assert app("Hello, world!") == "Hello, world!"
