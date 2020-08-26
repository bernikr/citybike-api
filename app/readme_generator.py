import os


def get_description():
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../readme.md", "r") as f:
        readme = f.readlines()
        readme[4] = "[Github project](https://github.com/bernikr/citybike-api)"
        return "\n".join(readme[1:])
