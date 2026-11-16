"""Compatibility entry point for the current tourism notebook."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('build_tourism_notebook.py')),run_name='__main__')
