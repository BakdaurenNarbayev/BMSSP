import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app import PathfindingTUI


def main():
    app = PathfindingTUI()
    app.run()


if __name__ == "__main__":
    main()
