from urllib.parse import urlparse


def is_url(string: str) -> bool:
    result = urlparse(string)
    return all([result.scheme, result.netloc])


def is_path(string: str) -> bool:
    result = urlparse(string)
    return not all([result.scheme, result.netloc])
