import pathlib
import os.path as osp
CWD = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIR = osp.join(CWD, "data")
OUTPUT_DIR = osp.join(CWD, "results")