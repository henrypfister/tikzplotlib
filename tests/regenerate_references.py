"""Regenerate all tikzplotlib test reference .tex files by monkey-patching assert_equality."""
import importlib
import pathlib
import sys

import matplotlib.pyplot as plt

# Ensure repo root is on path for tikzplotlib
repo_root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

import tikzplotlib

TEST_DIR = pathlib.Path(__file__).resolve().parent

# Monkey-patch assert_equality to write reference files
def _write_reference(plot, filename, assert_compilation=False, flavor="latex", **extra_get_tikz_code_args):
    plot()
    code = tikzplotlib.get_tikz_code(
        include_disclaimer=False,
        float_format=".8g",
        flavor=flavor,
        **extra_get_tikz_code_args,
    )
    plt.close("all")

    ref_path = TEST_DIR / filename
    with open(ref_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"  Wrote {ref_path.name}")


# Monkey-patch in the tests package namespace
import tests.helpers as helpers
helpers.assert_equality = _write_reference

# Now import and run each test module
if __name__ == "__main__":
    test_files = sorted(TEST_DIR.glob("test_*.py"))
    for test_file in test_files:
        module_name = f"tests.{test_file.stem}"
        print(f"Processing {module_name}...")
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "test"):
                mod.test()
            else:
                print(f"  No test() function, skipping.")
        except Exception as e:
            print(f"  ERROR: {e}")
            plt.close("all")

    print("Done regenerating references!")
