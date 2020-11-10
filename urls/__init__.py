import os


def projectRootDir():
    _init_dirname = os.path.dirname(__file__)
    project_dirname = os.path.dirname(_init_dirname)
    return project_dirname


ROOT = projectRootDir()

if __name__ == "__main__":
    print(projectRootDir())

