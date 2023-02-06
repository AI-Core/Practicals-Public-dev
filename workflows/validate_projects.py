import sys
from utils.client import Projects  # noqa: E402

# TODO move into projects repo

if __name__ == "__main__":
    projects = Projects()
    projects.validate()
