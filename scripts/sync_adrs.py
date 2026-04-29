from pathlib import Path
import shutil
import subprocess
import tempfile

import yaml


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_FILE = ROOT / "adr-registry.yml"
AGGREGATED_DIR = ROOT / "docs" / "aggregated"


def load_registry() -> list[dict]:
    with REGISTRY_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    projects = data.get("projects")
    if not isinstance(projects, list):
        raise ValueError("adr-registry.yml must contain a top-level 'projects' list")

    return projects


def reset_aggregated_dir() -> None:
    if AGGREGATED_DIR.exists():
        shutil.rmtree(AGGREGATED_DIR)
    AGGREGATED_DIR.mkdir(parents=True, exist_ok=True)


def clone_repo(repo_url: str, target_dir: Path) -> None:
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
        check=True,
    )


def sync_project(project: dict) -> None:
    project_id = project["id"]
    repo_url = project["repo"]
    adr_path = Path(project["adr_path"])

    # Expect adr_path like docs/adr
    if len(adr_path.parts) < 2 or adr_path.parts[0] != "docs":
        raise ValueError(
            f"Project '{project_id}': adr_path must be under docs/, got '{adr_path}'"
        )

    docs_dir = adr_path.parent  # docs
    source_adr_dir_name = adr_path.name  # adr

    with tempfile.TemporaryDirectory() as tmp:
        repo_dir = Path(tmp) / "repo"
        clone_repo(repo_url, repo_dir)

        source_docs_dir = repo_dir / docs_dir
        if not source_docs_dir.exists():
            raise FileNotFoundError(
                f"Project '{project_id}': source docs directory not found: {source_docs_dir}"
            )

        source_adr_dir = repo_dir / adr_path
        if not source_adr_dir.exists():
            raise FileNotFoundError(
                f"Project '{project_id}': ADR directory not found: {source_adr_dir}"
            )

        target_project_dir = AGGREGATED_DIR / project_id
        target_adr_dir = target_project_dir / source_adr_dir_name

        # Copy ADRs under aggregated/<project>/adr/
        shutil.copytree(source_adr_dir, target_adr_dir, dirs_exist_ok=True)

        # Copy docs/assets if present under aggregated/<project>/assets/
        source_assets_dir = source_docs_dir / "assets"
        if source_assets_dir.exists():
            target_assets_dir = target_project_dir / "assets"
            shutil.copytree(source_assets_dir, target_assets_dir, dirs_exist_ok=True)

        print(f"Synced project '{project_id}'")
        print(f"  ADRs:    {source_adr_dir} -> {target_adr_dir}")
        if source_assets_dir.exists():
            print(f"  Assets:  {source_assets_dir} -> {target_project_dir / 'assets'}")
        else:
            print("  Assets:  none")


def main() -> None:
    projects = load_registry()
    reset_aggregated_dir()

    for project in projects:
        sync_project(project)


if __name__ == "__main__":
    main()
