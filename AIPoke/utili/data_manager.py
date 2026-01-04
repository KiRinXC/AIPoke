import json
import os
from AIPoke.utili.path_manager import DATA_DIR

RIO_DET_FILE_NAME = "rio_det.json"
RIO_MOUSE_FILE_NAME= "rio_mouse.json"
CFG_KEY_FILE_NAME = "cfg_key.json"
CFG_USER_FILE_NAME = "cfg_user.json"

def _load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

RIO_DET = _load(os.path.join(DATA_DIR, RIO_DET_FILE_NAME))
RIO_MOUSE =_load(os.path.join(DATA_DIR, RIO_MOUSE_FILE_NAME))
CFG_KEY=_load(os.path.join(DATA_DIR, CFG_KEY_FILE_NAME))
CFG_USER=_load(os.path.join(DATA_DIR, CFG_USER_FILE_NAME))



