"""Shared test helpers for loading stdlib-only skill tools by file path.

Skill tools live under skills/<name>/scripts/*.py and are not packaged, so we
load them by absolute path with importlib. This keeps the tools dependency-free
while remaining fully testable.
"""
import importlib.util
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def load_tool(skill, module):
    """Import skills/<skill>/scripts/<module>.py and return the module."""
    path = SKILLS_DIR / skill / "scripts" / f"{module}.py"
    spec = importlib.util.spec_from_file_location(f"{skill}_{module}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
