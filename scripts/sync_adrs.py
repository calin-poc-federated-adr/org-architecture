from pathlib import Path
import shutil
import subprocess
import tempfile

import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"
REGISTRY_FILE = ROOT_DIR / "adr-registry.yml"


def load_registry():
    with REGISTRY_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def extract_title(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def clone_repo(owner: str, repo: str, branch: str, target_dir: Path) -> None:
    repo_url = f"https://github.com/{owner}/{repo}.git"
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


def build_repo_url(owner: str, repo: str, branch: str, adr_path: str) -> str:
    return f"https://github.com/{owner}/{repo}/tree/{branch}/{adr_path}"


def main() -> None:
    registry = load_registry()
    owner = registry["organization"]

    with tempfile.TemporaryDirectory() as temp_root:
        temp_root_path = Path(temp_root)

        for project in registry["projects"]:
            display_name = project["display_name"]
            repo = project["repo"]
            branch = project["branch"]
            adr_path = project["adr_path"]
            site_path = project["site_path"]

            repo_checkout_dir = temp_root_path / repo
            clone_repo(owner, repo, branch, repo_checkout_dir)

            source_dir = repo_checkout_dir / adr_path
            if not source_dir.exists():
                raise FileNotFoundError(
                    f"ADR path not found for {repo}: {source_dir}"
                )

            adr_files = sorted(
                file for file in source_dir.glob("*.md")
                if file.name.lower() != "readme.md"
            )

            target_dir = DOCS_DIR / site_path
            reset_directory(target_dir)

            overview_lines = [
                f"# {display_name} ADRs",
                "",
                f"Source repository: [{owner}/{repo}](https://github.com/{owner}/{repo})",
                "",
                f"Source ADR path: [{adr_path}]({build_repo_url(owner, repo, branch, adr_path)})",
                "",
                "## ADRs",
                "",
            ]

            for adr_file in adr_files:
                content = adr_file.read_text(encoding="utf-8")
                target_file = target_dir / adr_file.name
                target_file.write_text(content, encoding="utf-8")

                title = extract_title(content, adr_file.stem)
                overview_lines.append(f"- [{title}]({adr_file.name})")

            if not adr_files:
                overview_lines.append("_No ADR files found._")

            overview_lines.append("")
            (target_dir / "index.md").write_text(
                "\n".join(overview_lines),
                encoding="utf-8",
            )

            print(f"Synchronized {display_name} ADRs into {target_dir}")

    print("ADR synchronization complete.")


if __name__ == "__main__":
    main()