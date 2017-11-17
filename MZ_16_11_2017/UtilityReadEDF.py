# Script is for reading *.edf files exported from EEG DigiTrack Elmiko's amplifier with addition of information
# about appropriate sampling rate drawn from *.1 file, as well as information about the time of starting
# the signal recording took from file *.evx.

import glob
import struct
import xml.etree.ElementTree as etree
import pandas as pd
import numpy as np


def get_exact_sampling_rate(path):
    """
    Read exact sampling rate of the recorded signal from *.1 file.
    :param path: path to directory with only one *.1 file or directly to *.1 file.
    :return: (float) exact sampling rate.
    """

    # Open *.1 file.
    if path.endswith(".1"):
        binary_file = open(path, "rb")
    else:
        binary_file = open(glob.glob(path + "*.1")[0], "rb")

    # Get exact sampling rate from *.1 file.
    power_of_two = 32
    binary_file.seek(490 + (89 * power_of_two))
    couple_bytes = binary_file.read(8)
    sampling_rate = struct.unpack('d', couple_bytes)

    return sampling_rate[0]


def read_xml(path):
    """
    Read time of first EEG sample from *.evx file.
    :param path: path to directory with only one *.evx file or directly to *.evx file.
    :return: (DataFrame) time of rist EEG sample.
    """

    # Open *.evx file.
    if path.endswith("*.evx"):
        xml_file = open(path, mode='r', encoding="utf-8")
    else:
        xml_file = open(glob.glob(path + "*.evx")[0], mode='r', encoding="utf-8")

    # Get root xml element.
    xml_tree = etree.parse(xml_file)
    root = xml_tree.getroot()

    # Store this information in a data-frame in a datetime/timestamp format.
    df = pd.DataFrame()
    for child_of_root in root:

        if child_of_root.attrib["strId"] == "Technical_ExamStart":

            time_event = child_of_root.find("event")

            # Timestamp in unix time.
            unix_time = time_event.attrib["time"]

            # Timestamp in DateTime.
            dt_time = time_event.find("info").attrib["time"]

            timezone_info = dt_time.find('+')
            df["UNIXTIME"] = pd.to_datetime([unix_time], unit="us").tz_localize("UTC") + \
                             pd.Timedelta(hours=int(dt_time[timezone_info + 1: dt_time.find('+') + 3]))

            df["DateTime"] = pd.to_datetime([dt_time], infer_datetime_format=True).tz_localize('UTC') + \
                             pd.Timedelta(hours=int(dt_time[timezone_info + 1: dt_time.find('+') + 3]))

    return df


def exact_timestamp(path, n_samples, sampling_rate):
    """
    Create exact timestamp vector based on exact sampling rate and exact number of samples in EEG signal.
    :param path: path to directory with only one *.evx file or directly to *.evx file.
    :param n_samples: number of samples in EEG signal.
    :param sampling_rate: exact sampling rate of EEG signal.
    :return: timestampt vector.
    """

    # Exact sample duration in nanoseconds.
    exact_sample_ns = int(1000.0 / sampling_rate * 10**6)

    # Create time vector for nanosecond-precision date-times.
    timestamp = np.empty(n_samples, dtype="datetime64[ns]")

    # Set the first value using the first sample time saved by DigiTrack in *.evx file.
    df = read_xml(path)
    print("INFO", df)
    timestamp[0] = read_xml(path)["DateTime"].iloc[0]

    # Populate the time vector by adding sample duration to the next sample.
    for i in range(n_samples - 1):
        timestamp[i+1] = timestamp[i] + np.timedelta64(exact_sample_ns, "ns")

    return timestamp
