import shutil
from pathlib import Path

import importlib_resources


def prepare_workspace_environment():
    root_path = Path(__file__).parent.parent.parent

    env_path = root_path / '.env'
    home_path = root_path / "clsiwidgets"
    data_path = home_path / "data"
    results_path = home_path / "results"
    assets_path = home_path / "assets"

    results_path.mkdir(parents=True, exist_ok=True)

    # if not (data_path.exists() and any(data_path.iterdir())):
    #     copy_from_installed_wheel("clsiwidgets.data", resource="", dest_path=data_path)

    return {
        "env_path": env_path if env_path.exists() else None,
        "home_path": home_path,
        "data_path": data_path,
        "results_path": results_path,
        "assets_path": assets_path,
    }


def copy_from_installed_wheel(package_name, resource="", dest_path=None):
    """
    Copy directory from installed package to destination path.
    """
    if dest_path is None:
        dest_path = package_name.split(".")[-1]

    dest_path = Path(dest_path).expanduser().resolve()

    # Get the resource reference
    ref = importlib_resources.files(package_name)
    if resource:
        ref = ref.joinpath(resource)

    # Create the temporary folder context
    with importlib_resources.as_file(ref) as resource_path:
        resource_path = Path(resource_path).resolve()

        if not resource_path.is_dir():
            raise ValueError(
                f"Resource '{resource}' in package '{package_name}' is not a directory."
            )

        if resource_path == dest_path:
            return dest_path

        shutil.copytree(resource_path, dest_path, dirs_exist_ok=True)

    return dest_path
