import importlib.util
import sys
from pathlib import Path


def main():
    src_main = Path(__file__).resolve().parent / "src" / "main.py"
    src_dir = str(src_main.parent)
    spec = importlib.util.spec_from_file_location("pyvoxels_app_main", src_main)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load entrypoint from {src_main}")

    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, src_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == src_dir:
            sys.path.pop(0)

    module.main()


if __name__ == "__main__":
    main()
