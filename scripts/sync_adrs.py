from pathlib import Path
import shutil
import subprocess
import tempfile

import yaml


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_FILE = ROOT / "adr-registry.yml"
DOCS_DIR = ROOT / "docs"


def load_registry() -> dict:
    with REGISTRY_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("adr-registry.yml must contain a YAML object at the top level")

    if "projects" not in data or not isinstance(data["projects"], list):
        raise ValueError("adr-registry.yml must contain a top-level 'projects' list")

    return data


def reset_aggregated_dirs(projects: list[dict]) -> None:
    for project in projects:
        site_path = project.get("site_path")
        if not site_path:
            raise ValueError("Each project must define 'site_path'")

        target_dir = DOCS_DIR / site_path
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)


def build_repo_url(organization: str, repo_value: str) -> str:
    repo_value = repo_value.strip()

    if repo_value.startswith("https://") or repo_value.startswith("http://"):
        return repo_value

    return f"https://github.com/{organization}/{repo_value}.git"


def clone_repo(repo_url: str, branch: str, target_dir: Path) -> None:
    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            branch,
            repo_url,
            str(target_dir),
        ],
        check=True,
    )


def sync_project(organization: str, project: dict) -> None:
    key = project.get("key")
    repo_value = project.get("repo")
    branch = project.get("branch", "main")
    adr_path_value = project.get("adr_path")
    site_path_value = project.get("site_path")

    missing = [
        name
        for name, value in [
            ("key", key),
            ("repo", repo_value),
            ("adr_path", adr_path_value),
            ("site_path", site_path_value),
        ]
        if not value
    ]
    if missing:
        raise ValueError(
            f"Project entry is missing required field(s): {', '.join(missing)}"
        )

    adr_path = Path(adr_path_value)
    site_path = Path(site_path_value)

    # Expect adr_path like docs/adr
    if len(adr_path.parts) < 2 or adr_path.parts[0] != "docs":
        raise ValueError(
            f"Project '{key}': adr_path must start with 'docs/', got '{adr_path_value}'"
        )

    repo_url = build_repo_url(organization, repo_value)

    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = Path(tmp) / "repo"
        clone_repo(repo_url, branch, repo_dir)

        source_adr_dir = repo_dir / adr_path
        if not source_adr_dir.exists():
            raise FileNotFoundError(
                f"Project '{key}': ADR directory not found: {source_adr_dir}"
            )

        source_docs_dir = repo_dir / "docs"
        source_assets_dir = source_docs_dir / "assets"

        target_project_dir = DOCS_DIR / site_path
        target_adr_dir = target_project_dir / adr_path.name  # usually "adr"

        # Copy ADRs into docs/<site_path>/adr/
        shutil.copytree(source_adr_dir, target_adr_dir, dirs_exist_ok=True)

        # Copy docs/assets into docs/<site_path>/assets/ if present
        if source_assets_dir.exists():
            target_assets_dir = target_project_dir / "assets"
            shutil.copytree(source_assets_dir, target_assets_dir, dirs_exist_ok=True)

        print(f"Synced project '{key}'")
        print(f"  Repo URL: {repo_url}")
        print(f"  Branch:   {branch}")
        print(f"  ADRs:     {source_adr_dir} -> {target_adr_dir}")
        if source_assets_dir.exists():
            print(f"  Assets:   {source_assets_dir} -> {target_project_dir / 'assets'}")
        else:
            print("  Assets:   none")


def main() -> None:
    registry = load_registry()
    organization = registry.get("organization")
    projects = registry["projects"]

    if not organization:
        raise ValueError("adr-registry.yml must contain 'organization'")

    reset_aggregated_dirs(projects)

    for project in projects:
        sync_project(organization, project)


if __name__ == "__main__":
    main()
