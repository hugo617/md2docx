import requests


def down_image(img_url: str, save_file_path: str) -> None:
    resp = requests.get(img_url, timeout=30)
    resp.raise_for_status()
    with open(save_file_path, "wb") as f:
        f.write(resp.content)
