"""Constants."""
import os
from datetime import datetime
import pytz

CONTAINER_DIR = '/app'
OUTPUT_DIR = "./cache"
ALT_PROCESSING_DIR = './Dropbox/COVID19/chime'
ALT_OUTPUT_DIR = "./output"

PARAMETERS_FILE = ALT_PARAMETERS_FILE = "./parameters/params.txt"

SD_MODEL_DIR = './parameters/sd'

class ChimeCLIEnvironment :
    """Arbitrary regions to sum population."""

    def __init__(self):

        self.sd_model_dir = SD_MODEL_DIR + "/"

        if os.getcwd() == CONTAINER_DIR :
            self.output_dir = OUTPUT_DIR
            self.parameters_file = PARAMETERS_FILE
            self.inContainer = True
        else :
            self.inContainer = False
            self.output_dir = ALT_OUTPUT_DIR
            self.parameters_file = ALT_PARAMETERS_FILE
            os.chdir(ALT_PROCESSING_DIR)

        if not os.path.exists(SD_MODEL_DIR):
            os.mkdir(SD_MODEL_DIR)

        tz_NY = pytz.timezone('America/New_York')
        t = datetime.now(tz_NY).strftime("/%Y%m%d-%H%M%S")

        self.run_datetime = datetime.now(tz_NY)
        self.output_dir += t
        os.mkdir(self.output_dir)
