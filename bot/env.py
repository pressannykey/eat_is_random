import os
from pathlib import Path

from dotenv import load_dotenv

THIS_DIR = Path(__file__).absolute().parent

DOTENV_PATH = THIS_DIR.parent / '.env'

if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)
