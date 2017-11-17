import mne
from MZ_16_11_2017 import UtilityReadEDF as read_edf
import numpy as np
import scipy.io as sio

# Path to directory with raw data.
path_to_raw_data = "Data/raw/"

# Path to directory with prepared data.
path_to_prep_data = "Data/prepared/"

# Load *.edf files.
mne_raw = mne.io.read_raw_edf(path_to_raw_data + "data-raw.edf", stim_channel=None, preload=True)
mne_filt_reref = mne.io.read_raw_edf(path_to_raw_data + "data-filtered-re-referenced.edf", stim_channel=None, preload=True)

# Get exact sampling rate. In default, *.edf file contains sampling rate chosen by the user during the recording
# in the DigiTrack recording software - this value is inaccurate. The accurate and real value of the sampling rate
# is stored in *.1 file.
exact_sr = read_edf.get_exact_sampling_rate(path_to_raw_data)

# Replace old sampling rate with the new one.
mne_raw.info.update({"sfreq": exact_sr})
mne_filt_reref.info.update({"sfreq": exact_sr})

# Save data as *.npy.
np.save(path_to_prep_data + "data-raw.npy", mne_raw[:][0])
np.save(path_to_prep_data + "data-filtered-re-referenced.npy", mne_filt_reref[:][0])

# Save data as *.mat.
sio.savemat(path_to_prep_data + "data-raw.mat", mdict={"data": mne_raw[:][0]})
sio.savemat(path_to_prep_data + "data-filtered-re-referenced.mat", mdict={"data": mne_filt_reref[:][0]})
