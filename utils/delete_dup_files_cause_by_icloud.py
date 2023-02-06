from pathlib import Path
import os


def generate_path_expressions():
    for extension in ["yaml", "md", "py", "ipynb", "png", "txt", "json", "joblib", "JPG", "pdf", "jpg", "key", "webp", "gif", "jpeg", "svg"]:
        for idx in range(2, 10):
            path_exp = f"* {idx}.{extension}"
            yield path_exp
            path_exp += ".icloud"
            yield path_exp
            # path_exp = f"* {idx}" # TODO delete dup folders


if __name__ == "__main__":
    for path_expression in generate_path_expressions():
        dups = Path(".").rglob(path_expression)
        dups = [str(d) for d in dups]
        for dup in dups:
            print(dup)
            os.remove(dup)
