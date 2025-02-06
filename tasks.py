import os
from pathlib import Path
import shutil
import invoke


@invoke.task
def black(ctx):
    """
    Format file using black.
    """
    python_files = [file.as_posix() for file in Path("./").rglob("*.py")]
    run(f"black {' '.join(python_files)}")


@invoke.task
def exe(ctx):
    """
    Generate exe using pyinstaller.
    """
    run("pyinstaller.exe defect_localisation_sbc\cli.py -F -n defect_localisation_sbc")


@invoke.task(optional=["proxy"])
def wheelhouse(ctx, proxy=None):
    """
    Download dependencies wheel and store them locally.
    """
    if proxy:
        set_proxy()
    run(
        "pip wheel . --wheel-dir .\wheelhouse --extra-index-url https://suezsmartsolutions.pkgs.visualstudio.com/AQDV-UD/_packaging/AquadvancedUrbanDrainage/pypi/simple/"
    )


@invoke.task
def clean(ctx):
    """
    Remove all temporary files and directory.
    """
    remove_files_with_extension("./", "**/log.txt")
    clean_build()
    clean_artifact()
    clean_tests()


@invoke.task
def coverage(ctx):
    """
    Check code coverage using pytest.
    """
    run("python -m coverage run --source defect_localisation_sbc -m pytest")
    run("python -m coverage report -m")
    run("python -m coverage html")


@invoke.task
def doc_build(ctx):
    """
    Build the documentation
    """
    run("mkdocs build --clean")


@invoke.task
def doc_edit(ctx):
    """
    Run interactive server to visualize the documentation.
    """
    run("mkdocs serve")


def set_proxy():
    """
    Set proxy environnement variable.
    """
    os.environ["http_proxy"] = f"{proxy}"
    os.environ["https_proxy"] = f"{proxy}"


def run(command):
    """Run command using invoke run

    Args:
        command (str): Shell command to run
    """
    print(command)
    invoke.run(command)


def clean_build():
    """Clean all temporary files and folder used to build the package."""
    remove_directory("./dist")
    remove_directory("./build")
    remove_directory("./eggs")
    remove_directory("./.eggs")
    remove_dir_with_extension("./", "*.egg-info")
    remove_files_with_extension("./", "**/*.egg")


def clean_artifact():
    """Clean all python artifact."""
    remove_files_with_extension("./", "**/*.pyc")
    remove_files_with_extension("./", "**/*.pyo")
    remove_dir_with_extension("./", "**/*__pycache__")


def clean_tests():
    """Clean all temporary files and folder used by pytest."""
    remove_directory("./tox")
    remove_directory("./htmlcov")
    remove_directory(".pytest_cache")


def get_path_with_pattern(path, pattern):
    return list(Path(path).glob(pattern))


def remove_directory(path):
    dir_path = Path(path)
    if dir_path.is_dir():
        print(f"Removing {dir_path}")
        shutil.rmtree(dir_path)


def remove_dir_with_extension(path, ext):
    for i_path in get_path_with_pattern(path, ext):
        if i_path.is_dir():
            print(f"Removing directory {i_path}")
            shutil.rmtree(i_path)


def remove_files_with_extension(path, ext):
    for file in get_path_with_pattern(path, ext):
        if file.is_file():
            print(f"Removing {file}")
            file.unlink()
