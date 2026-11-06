"""PyCharm entry point: opens the local Streamlit app."""
import subprocess
import sys
import os
from pathlib import Path
def launch(version=None):
    root = Path(__file__).resolve().parent
    command = [sys.executable, '-m', 'streamlit', 'run', str(root / 'app.py'),
               '--server.address=localhost']
    environment = os.environ.copy()
    environment['IBIRAPUERA_SCREEN'] = version or ''
    subprocess.run(command, cwd=root, env=environment, check=True)


if __name__ == '__main__':
    launch()
