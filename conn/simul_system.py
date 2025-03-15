from db.storage_sqlite import Storage  # Assuming hrt_storage.py exists
# from db.storage_xlsx import Storage  # Assuming hrt_storage.py exists
from hrt.hrt_type import hrt_type_hex_to, hrt_type_hex_from  # Assuming hrt_type.py exists
from hrt.old.hrt_settings import hrt_settings
from asteval import Interpreter
from ctrl.simul_tf import SimulTf
from typing import Union
import pandas as pd
import re
from hrt.hrt_data import HrtData


class SimulSystem():

    def __init__(self, hrt_data:HrtData):
        self._hrt_data = hrt_data