"""
This module contains functions for handling the current trajectory summary data_models schema.
"""
import json
import os
import tempfile

import pandavro as pdx
from avro.datafile import DataFileReader
from avro.io import DatumReader

import gmn_python_api


SCHEMA_VERSION = "2.0"
""""""

_MODEL_TRAJECTORY_SUMMARY_FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "data_models",
    "traj_summary_20220304_solrange_344.0-345.0.txt",
)
"""Model v2.0 trajectory summary file."""

_AVRO_PATH = os.path.join(tempfile.gettempdir(), "trajectory_summary.avro")
""""""

_AVSC_PATH = os.path.join(
    tempfile.gettempdir(), f"trajectory_summary_schema_{SCHEMA_VERSION}.avsc"
)
""""""


def get_trajectory_summary_avro_schema() -> dict:
    """
    Get the Avro schema (.avsc) for the current trajectory summary data format.
    :return: The Avro schema in .avsc format.
    """
    data_frame = gmn_python_api.read_trajectory_summary_as_dataframe(
        _MODEL_TRAJECTORY_SUMMARY_FILE_PATH, camel_case_column_names=True
    )
    data_frame.reset_index(inplace=True)
    data_frame.rename(
        columns={"Unique trajectory (identifier)": "unique_trajectory_identifier"},
        inplace=True,
    )
    data_frame.iau_code = data_frame.iau_code.astype("unicode")
    data_frame.schema_version = data_frame.schema_version.astype("unicode")

    pdx.to_avro(_AVRO_PATH, data_frame)
    pdx.read_avro(_AVRO_PATH)

    reader = DataFileReader(open(_AVRO_PATH, "rb"), DatumReader())
    schema = json.loads(reader.meta["avro.schema"].decode())

    return schema