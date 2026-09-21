import os
from pathlib import Path

class BaseDir():

    def __init__(self) -> None:
        self.directory = None

    def get_base_directory(self) -> str:
        return Path(__file__).resolve().parent.parent.parent


if __name__ == "__main__":
    dir = BaseDir()
    print(dir.get_base_directory())
    # Print (C:\Users\Vivek\GIT Projects\MultiLinguinal_Application\Backend\)