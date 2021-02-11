import os


def projectRootDir():
    _init_dirname = os.path.dirname(__file__)
    project_dirname = os.path.dirname(_init_dirname)
    return project_dirname


ROOT = projectRootDir()
KEYS_DIR = f"{ROOT}/resources/keys"
LOG_DIR = f"{ROOT}/resources/logs"
SETTINGS_DIR = f"{ROOT}/resources/settings"

if __name__ == "__main__":
    print(projectRootDir())

