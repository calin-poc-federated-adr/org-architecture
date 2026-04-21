from pathlib import Path
from urllib.request import urlopen
import shutil

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


def download_text(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode("utf-8")


def extract_title(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_raw_url(owner: str, repo: str, branch: str, adr_path: str, filename: str) -> str:
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{adr_path}/{filename}"


def build_repo_url(owner: str, repo: str, branch: str, adr_path: str) -> str:
    return f"https://github.com/{owner}/{repo}/tree/{branch}/{adr_path}"


def main() -> None:
    registry = load_registry()
    owner = registry["organization"]

    for project in registry["projects"]:
        display_name = project["display_name"]
        repo = project["repo"]
        branch = project["branch"]
        adr_path = project["adr_path"]
        site_path = project["site_path"]
        files = project["files"]

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

        for filename in files:
            url = build_raw_url(owner, repo, branch, adr_path, filename)
            markdown_text = download_text(url)

            output_file = target_dir / filename
            output_file.write_text(markdown_text, encoding="utf-8")

            title = extract_title(markdown_text, filename.replace(".md", ""))
            overview_lines.append(f"- [{title}]({filename})")

        overview_lines.append("")
        (target_dir / "index.md").write_text("\n".join(overview_lines), encoding="utf-8")

        print(f"Synchronized {display_name} ADRs into {target_dir}")

    print("ADR synchronization complete.")


if __name__ == "__main__":
    main()
