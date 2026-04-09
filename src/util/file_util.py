import os
import shutil
import uuid
from typing import Optional, Tuple

from . import str_util, net_util


def read(filepath: str) -> str:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write(filepath: str, data: str) -> None:
    dirpath = os.path.dirname(filepath)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(data)


def get_abspath(basefile: str, filepath: str) -> str:
    return os.path.normpath(os.path.join(os.path.dirname(basefile), filepath))


def get_image_to_target(
    link: str, from_filepath: str, target_foldpath: str
) -> Tuple[str, bool]:
    name = uuid.uuid4().hex + "." + link.split(".")[-1]
    if str_util.is_url(link):
        net_util.down_image(link, os.path.join(target_foldpath, name))
    else:
        if not os.path.isabs(link):
            link = get_abspath(from_filepath, link)
        if not os.path.exists(link):
            return "", True
        shutil.copyfile(link, os.path.join(target_foldpath, name))
    return name, False


def get_files_under_folder(
    folderpath: str, suffix_name: Optional[str] = None
) -> list[str]:
    return [
        os.path.abspath(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(folderpath)
        for filename in filenames
        if suffix_name is None or filename.endswith("." + suffix_name)
    ]
