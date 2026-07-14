from pathlib import Path
import os
import sys


APP_DIRNAME = "RYP_APP"
FRAMEWORK_WORKSPACE_DIRNAME = "workspace"
PRIVATE_ASSETS_ENV_VAR = "RYP_PRIVATE_ASSETS_ROOT"
STANDALONE_MODE_ENV_VAR = "RYP_FRAMEWORK_STANDALONE"
FRAMEWORK_WORKSPACE_ENV_VAR = "RYP_FRAMEWORK_WORKSPACE_ROOT"


def is_frozen():
    return getattr(sys, "frozen", False)


def is_standalone_mode():
    raw = os.environ.get(STANDALONE_MODE_ENV_VAR, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def get_framework_root():
    return Path(__file__).resolve().parent.parent


def get_resource_root():
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    # ryp_framework/utils/paths.py is 3 levels below the project root
    return Path(__file__).resolve().parent.parent.parent


def get_launch_root():
    if is_frozen():
        return Path(sys.executable).resolve().parent
    # ryp_framework/utils/paths.py is 3 levels below the project root
    return Path(__file__).resolve().parent.parent.parent


def get_user_data_root(app_name=APP_DIRNAME):
    if is_frozen():
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            root = Path(local_appdata) / app_name
        else:
            root = get_launch_root() / app_name
    else:
        root = get_launch_root()
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_framework_workspace_root(create=False):
    configured = os.environ.get(FRAMEWORK_WORKSPACE_ENV_VAR, "").strip()
    if configured:
        root = Path(configured).expanduser()
    elif is_frozen():
        # In one-file executables, package files are extracted under a temporary
        # _MEI folder. Runtime workspace must be persistent outside temp.
        root = get_user_data_root(app_name="RYP_Framework") / FRAMEWORK_WORKSPACE_DIRNAME
    else:
        root = get_framework_root() / FRAMEWORK_WORKSPACE_DIRNAME
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def get_framework_workspace_path(*parts, create_parent=True):
    path = get_framework_workspace_root(create=create_parent).joinpath(*parts)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_documents_root():
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        return Path(userprofile) / "Documents"
    return Path.home() / "Documents"


def get_private_assets_root(create=False):
    if is_standalone_mode():
        root = get_framework_workspace_path("private_assets", create_parent=False)
        if create:
            root.mkdir(parents=True, exist_ok=True)
        return root
    configured = os.environ.get(PRIVATE_ASSETS_ENV_VAR, "").strip()
    root = Path(configured).expanduser() if configured else get_documents_root() / "RYP" / "private_assets"
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def get_private_asset_path(container, *parts, prefer_private=False):
    local_path = get_resource_root().joinpath(container, *parts)
    private_path = get_private_assets_root().joinpath(container, *parts)
    if local_path.exists() and not prefer_private:
        return local_path
    if private_path.exists():
        return private_path
    return private_path if prefer_private else local_path


def get_documentation_original_path(*parts, prefer_private=False):
    if is_standalone_mode():
        return get_framework_workspace_path("DOCUMENTACION_ORIGINAL", *parts)
    return get_private_asset_path("DOCUMENTACION ORIGINAL", *parts, prefer_private=prefer_private)


def get_papers_q1_path(*parts, prefer_private=False):
    if is_standalone_mode():
        return get_framework_workspace_path("PAPERS_Q1", *parts)
    return get_private_asset_path("PAPERS_Q1", *parts, prefer_private=prefer_private)


def get_resource_path(*parts):
    return get_resource_root().joinpath(*parts)


def get_user_data_path(*parts, app_name=APP_DIRNAME, create_parent=True):
    path = get_user_data_root(app_name=app_name).joinpath(*parts)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path
