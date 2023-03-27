__author__ = "Clea Parcerisas"
__version__ = "0.1"
__credits__ = "Clea Parcerisas"
__email__ = "clea.parcerisas@vliz.be"
__status__ = "Development"

import datetime
import os
import pathlib
import zipfile

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import soundfile as sf

from pypam import signal as sig
from pypam import acoustic_file

pd.plotting.register_matplotlib_converters()
plt.rcParams.update({'pcolor.shading': 'auto'})

# Apply the default theme
sns.set_theme()


class Detection(sig.Signal):
    """
    Detection recorded in a wav file, with start and end

    Parameters
    ----------
    sfile : Sound file
        Can be a path or a file object
    hydrophone : Object for the class hydrophone
    p_ref : Float
        Reference pressure in upa
    timezone: datetime.tzinfo, pytz.tzinfo.BaseTZInfo, dateutil.tz.tz.tzfile, str or None
        Timezone where the data was recorded in
    channel : int
        Channel to perform the calculations in
    calibration: float, -1 or None
        If it is a float, it is the time ignored at the beginning of the file. If None, nothing is done. If negative,
        the function calibrate from the hydrophone is performed, and the first samples ignored (and hydrophone updated)
    dc_subtract: bool
        Set to True to subtract the dc noise (root mean squared value
    start_seconds: float
        Seconds from start where the detection starts
    end_seconds: float
        Seconds from start where the detection ends
    """

    def __init__(self, start_seconds, end_seconds, sfile, hydrophone, p_ref, timezone='UTC', channel=0,
                 calibration=None, dc_subtract=False):

        self.acu_file = acoustic_file.AcuFile(sfile, hydrophone, p_ref, timezone=timezone, channel=channel,
                                              calibration=calibration, dc_subtract=dc_subtract)
        self.start_seconds = start_seconds
        self.end_seconds = end_seconds

        self.frame_init = int(self.acu_file.fs * self.start_seconds)
        self.frame_end = int(self.acu_file.fs * self.end_seconds)

        self.frames = self.frame_end - self.frame_init

        self.duration = self.end_seconds - self.start_seconds

        wav_sig, fs = sf.read(self.acu_file.file_path, start=self.frame_init, stop=min(self.frame_end,
                                                                                       self.acu_file.file.frames))

        # Read the signal and prepare it for analysis
        signal_upa = self.acu_file.wav2upa(wav=wav_sig)
        super().__init__(signal=signal_upa, fs=self.acu_file.fs, channel=self.acu_file.channel)
