"""
Basic project structure tests.
"""

import pytest
from pathlib import Path


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
        "data",
        "evidence",
        "scripts",
        "tests",
        "vendor",
    ]
    for dir_path in required_dirs:
        assert Path(dir_path).exists(), f"Missing directory: {dir_path}"


def test_required_files():
    """Verify required files exist."""
    required_files = [
        "instructions.md",
        "AGENTS.md",
        "README.md",
        "requirements.txt",
        "pyproject.toml",
        ".gitignore",
        ".pre-commit-config.yaml",
        "copilot-setup-steps.yml",
        "bridge/cost_model.py",
        "bridge/openalgo_nautilus.py",
        "scripts/gate_check.py",
        "research/calls.py",
        "research/grader.py",
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
    assert "Gate 0" in content
    assert "Gate 1" in content
    assert "Gate 2" in content
    assert "Gate 3" in content
    assert "Gate 4" in content
    assert "Gate 5" in content
    assert "Gate 6" in content


def test_agents_md_exists():
    """Verify AGENTS.md exists and has hard rules."""
    content = Path("AGENTS.md").read_text()
    assert "Hard rules" in content
    assert "Never place, enable or prepare a live order" in content
    assert "Paper only" in content or "paper-only" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])