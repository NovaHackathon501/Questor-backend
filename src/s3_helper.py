"""
Purpose : S3 utility — list all objects under a prefix and build a nested folder tree
"""

from config import s3_client, S3_BUCKET_NAME


def list_all_objects(prefix: str) -> list[str]:
    """
    Returns all S3 object keys under the given prefix.
    Handles pagination automatically.
    """
    keys = []
    paginator = s3_client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])

    return keys


def build_tree(keys: list[str], prefix: str) -> dict:
    """
    Converts a flat list of S3 keys into a nested folder tree dict.

    Example:
        keys = [
            "NCERT/class-9/Science/Chapter 1.pdf",
            "NCERT/class-9/Science/Chapter 2.pdf",
            "NCERT/class-9/English/Chapter 1.pdf",
        ]
        prefix = "NCERT/"

        Result:
        {
            "class-9": {
                "Science": ["Chapter 1.pdf", "Chapter 2.pdf"],
                "English": ["Chapter 1.pdf"]
            }
        }
    """
    tree = {}

    for key in keys:
        # Strip the root prefix (e.g. "NCERT/") from the key
        relative = key[len(prefix):]

        # Skip empty string (the folder itself)
        if not relative:
            continue

        parts = relative.split("/")

        # Navigate/create nested dicts for folder parts
        node = tree
        for part in parts[:-1]:          # all parts except the last (filename)
            node = node.setdefault(part, {})

        filename = parts[-1]

        # Skip S3 "folder" placeholder objects (empty key ending in /)
        if not filename:
            continue

        # At the leaf level, store filenames in a list
        if isinstance(node, dict):
            node.setdefault("_files", []).append(filename)

    return tree


def _sort_files(files: list[str]) -> list[str]:
    """
    Sort chapter files numerically, with special files (Prelims, Answers) at the end.
    e.g. Chapter 1, Chapter 2, ..., Chapter 12, Answers.pdf, Prelims.pdf
    """
    def sort_key(name):
        if name.startswith("Chapter "):
            try:
                return (0, int(name.replace("Chapter ", "").replace(".pdf", "")))
            except ValueError:
                pass
        return (1, name)  # non-chapter files go to end, alphabetically

    return sorted(files, key=sort_key)


def flatten_tree(tree: dict) -> dict:
    """
    Moves _files list up as a plain list value when a folder contains files.
    Produces a clean output without the internal _files key.

    Input:  {"class-9": {"Science": {"_files": ["Chapter 1.pdf"]}}}
    Output: {"class-9": {"Science": ["Chapter 1.pdf"]}}
    """
    result = {}
    for key, value in tree.items():
        if key == "_files":
            continue
        if isinstance(value, dict):
            files = value.pop("_files", [])
            nested = flatten_tree(value)
            if not nested and files:
                result[key] = _sort_files(files)
            elif nested and files:
                result[key] = {**nested, "_files": _sort_files(files)}
            elif nested:
                result[key] = nested
            else:
                result[key] = {}
        else:
            result[key] = value
    return result
