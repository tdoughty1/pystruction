from pathlib import Path
import subprocess
from jinja2 import Environment, PackageLoader, select_autoescape

TEMPLATE_ENV = Environment(
    loader=PackageLoader("pystruction"), autoescape=select_autoescape()
)


def add_dependencies(dependencies: list[str], group: str | None = None) -> None:
    if group:
        cmd_list = ["uv", "add", "--group", f"{group}", *dependencies]
    else:
        cmd_list = ["uv", "add", *dependencies]
    print(cmd_list)
    subprocess.run(cmd_list, check=False)
    print(f"Successfully added {dependencies}")


def copy_template(template_name: str, output_path: Path, **kwargs) -> None:
    template = TEMPLATE_ENV.get_template(template_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        template.render(kwargs),
        encoding="utf-8",
    )


def uv_run(*args) -> None:
    cmd_list = ["uv", "run", "--active"]
    cmd_list.extend(args)
    print(args)
    subprocess.run(args, check=False)
    print(f"Successfully ran {args}")


def initialize_project(python_version: str | None = 3.12) -> None:
    # Setup project structure with uv
    subprocess.run(["uv", "--version"], check=False)
    subprocess.run(
        ["uv", "init", "--app", "--package", "--python", "3.12", "--managed-python"],
        check=False,
    )


def initialize_git() -> None:
    cmd_list = ["git", "init"]
    subprocess.run(cmd_list, check=False)
    cmd_list = ["touch", ".gitignore"]
    subprocess.run(cmd_list, check=False)


def setup_testing(project_name) -> None:
    test_dir = Path("tests")
    test_dir.mkdir(exist_ok=True)
    test_init = test_dir / "__init__.py"
    test_init.touch()
    test_path = test_dir / "test_main.py"
    copy_template("test.txt", test_path, project_name=project_name)
    add_dependencies(["pytest", "pytest-cov"], "test")
    uv_run("pytest", "--version")
    print("Successfully setup testing")


def setup_linter() -> None:
    add_dependencies(["ruff"], "dev")
    uv_run("ruff", "--version")
    print("Successfully setup linter")


def setup_documentation() -> None:
    add_dependencies(["mkdocs-material", "pydoclint"], "docs")
    uv_run("mkdocs", "new", ".")


def setup_code_analysis() -> None:
    add_dependencies(["radon"], "dev")


def setup_interactivity() -> None:
    add_dependencies(["ipython"], "dev")


def setup_precommit(project_name) -> None:
    add_dependencies(["pre-commit"], "dev")
    copy_template(
        ".pre-commit-config.txt",
        Path(".pre-commit-config.yaml"),
        project_name=project_name,
    )
    uv_run(
        "pre-commit",
        "autoupdate",
        "--repo",
        "https://github.com/pre-commit/pre-commit-hooks",
    )
    uv_run(
        "pre-commit",
        "autoupdate",
        "--repo",
        "https://github.com/astral-sh/ruff-pre-commit",
    )
    uv_run("pre-commit", "run", "--all-files")


def setup_deployment(project_name) -> None:
    output_path = Path(".github") / "workflows" / "python-deployment.yml"
    copy_template("python-package.txt", output_path, project_name=project_name)
    add_dependencies(["python-semantic-release"], "dev")


def setup_security() -> None:
    add_dependencies(["bandit"], "dev")


def setup_recipes(project_name) -> None:
    copy_template("justfile.txt", Path("justfile"), project_name=project_name)


def setup_logging() -> None:
    add_dependencies(["loguru"])
