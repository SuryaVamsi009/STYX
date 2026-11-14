"""Basic project structure and configuration tests."""

from pathlib import Path

import pytest


def test_repo_structure():
    """Verify required directories exist."""
    required_dirs = [
        "bridge",
        "research",
        "research/snapshots",
        "research/playbook",
        "research/protocols",
        "strategies",
        "config",
        "evidence",
        "scripts",
        "tests",
    ]
    for dir_path in required_dirs:
        assert Path(dir_path).exists(), f"Missing directory: {dir_path}"


def test_required_files():
    """Verify required files exist."""
    required_files = [
        "instructions.md",
        "AGENTS.md",
        "README.md",
        "pyproject.toml",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".github/workflows/ci.yml",
        ".github/copilot-setup-steps.yml",
    ]
    for file_path in required_files:
        assert Path(file_path).exists(), f"Missing file: {file_path}"


def test_gitignore_excludes_secrets():
    """Verify .gitignore excludes sensitive files."""
    gitignore = Path(".gitignore").read_text()
    assert ".env" in gitignore
    assert "*.env" in gitignore
    assert "vendor/" in gitignore
    assert "data/" in gitignore
    assert ".venv-*" in gitignore


def test_instructions_has_gates():
    """Verify instructions.md contains gate definitions."""
    content = Path("instructions.md").read_text()
    # Gates are in a table format: "0. Scope and safety", "1. Data path", etc.
    assert "0. Scope and safety" in content
    assert "1. Data path" in content
    assert "2. Accounting" in content
    assert "3. Paper smoke test" in content
    assert "4. Operational safety" in content
    assert "5. Protocol freeze" in content
    assert "6. Evidence review" in content


def test_agents_md_exists():
    """Verify AGENTS.md exists and has hard rules."""
    content = Path("AGENTS.md").read_text()
    assert "Hard rules" in content
    assert "Never place, enable or prepare a live order" in content
    assert "Paper only" in content or "paper-only" in content.lower()


def test_pyproject_toml_valid():
    """Verify pyproject.toml has required configuration."""
    import tomllib

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)

    assert config["project"]["name"] == "pulse"
    assert config["project"]["requires-python"] == ">=3.12"
    assert "pandas" in config["project"]["dependencies"]
    assert "numpy" in config["project"]["dependencies"]
    assert "duckdb" in config["project"]["dependencies"]
    assert "dev" in config["dependency-groups"]
    assert "pytest" in config["dependency-groups"]["dev"]
    assert "ruff" in config["dependency-groups"]["dev"]
    assert "mypy" in config["dependency-groups"]["dev"]


def test_ci_yml_valid():
    """Verify CI workflow has required jobs."""
    import yaml

    with open(".github/workflows/ci.yml") as f:
        workflow = yaml.safe_load(f)

    assert "lint-and-test" in workflow["jobs"]
    assert "gate-check" in workflow["jobs"]
    assert "security" in workflow["jobs"]
    assert workflow["permissions"]["contents"] == "read"
    assert "concurrency" in workflow


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
