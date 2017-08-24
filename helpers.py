import os
import hashlib

from urllib.request import FancyURLopener


class MyOpener(FancyURLopener, object):
    version = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"


def get_data_folder(sub_dir):
    data_dir = os.path.join(os.getcwd(), "data")
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    data_sub_dir = os.path.join(data_dir, sub_dir)
    if not os.path.isdir(data_sub_dir):
        os.mkdir(data_sub_dir)

    return data_sub_dir


def default_logger(message):
    print(message)


def get_file_md5(file_path):
    with open(file_path, "rb") as f:
        image_bytes = f.read()

    file_hasher = hashlib.md5()
    file_hasher.update(image_bytes)
    return file_hasher.hexdigest()
