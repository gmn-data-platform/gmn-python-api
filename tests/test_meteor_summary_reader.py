"""Tests for the meteor_summary_reader module."""
import json
import os
import unittest
from pathlib import Path
from typing import Any

import numpy.typing as npt
import pandas as pd  # type: ignore
from avro_validator.schema import Schema  # type: ignore
from tests.expected_gmn_meteor_summary_reader_values import EXPECTED_COLUMN_NAMES
from tests.expected_gmn_meteor_summary_reader_values import (
    EXPECTED_COLUMN_NAMES_CAMEL_CASE,
)
from tests.expected_gmn_meteor_summary_reader_values import EXPECTED_DTYPES

from gmn_python_api import meteor_summary_reader as msr
from gmn_python_api.meteor_summary_schema import _MODEL_TRAJECTORY_SUMMARY_FILE_PATH
from gmn_python_api.meteor_summary_schema import get_meteor_summary_avro_schema


class TestGmnMeteorSummaryReader(unittest.TestCase):
    """Tests for the meteor_summary_reader module."""

    def setUp(self) -> None:
        """
        Sets up the tests.
        """
        self.test_data_directory_file_path1: Path = Path(
            _MODEL_TRAJECTORY_SUMMARY_FILE_PATH
        )

        self.test_data_directory_file_path2: Path = Path(
            os.path.join(
                os.path.dirname(__file__),
                "test_data",
                "traj_summary_monthly_201812.txt",
            )
        )

        self.test_rest_api_file_path: Path = Path(
            os.path.join(os.path.dirname(__file__), "test_data", "meteor_summary.txt")
        )

    def test_read_meteor_summary_csv_as_dataframe_str(self) -> None:
        """
        Test: That the model trajectory summary buffer can be read as a dataframe by
         checking properties.
        When: read_meteor_summary_csv_as_dataframe is called.
        """
        self._test_read_trajectory_summary_using_data_frame(
            msr.read_meteor_summary_csv_as_dataframe(
                open(self.test_data_directory_file_path1).read(),
                csv_data_directory_format=True,
            )
        )

    def test_read_meteor_summary_csv_as_dataframe_multiple(self) -> None:
        """
        Test: That a trajectory summary buffer can be read as a split up dataframe by
         checking properties.
        When: read_meteor_summary_csv_as_dataframe is called with a list of data.
        """
        data = open(self.test_data_directory_file_path1).read().splitlines()
        self._test_read_trajectory_summary_using_data_frame(
            msr.read_meteor_summary_csv_as_dataframe(
                ["\n".join(data[:40]), "\n".join(data[40:80]), "\n".join(data[80:])],
                csv_data_directory_format=True,
            )
        )

    def test_read_meteor_summary_csv_as_dataframe_multiple_with_headers(self) -> None:
        """
        Test: That a trajectory summary buffer can be read as a split up dataframe by
         checking properties.
        When: read_meteor_summary_csv_as_dataframe is called with a list of data with
         headers.
        """
        data1 = open(self.test_data_directory_file_path1).read().splitlines()
        data2 = open(self.test_data_directory_file_path2).read().splitlines()
        joined_dataframe = msr.read_meteor_summary_csv_as_dataframe(
            ["\n".join(data1[:12]), "\n".join(data2[:12])],
            csv_data_directory_format=True,
        )

        self.assertEqual(len(joined_dataframe.index), 4)

    def test_read_meteor_summary_csv_as_dataframe_multiple_rest_api_csv(self) -> None:
        """
        Test: That a trajectory summary buffer can be read as a split up dataframe by
         checking properties.
        When: read_meteor_summary_csv_as_dataframe is called with a list of REST data.
        """
        data = open(self.test_rest_api_file_path).read().splitlines()
        joined_dataframe = msr.read_meteor_summary_csv_as_dataframe(
            ["\n".join(data[:2]), data[0] + "\n" + "\n".join(data[2:4])],
            csv_data_directory_format=False,
        )

        self.assertEqual(len(joined_dataframe.index), 3)

    def test_read_meteor_summary_csv_as_dataframe_failed_type(self) -> None:
        """
        Test: That read_meteor_summary_csv_as_dataframe raises error with incorrect
         type.
        When: read_meteor_summary_csv_as_dataframe is called with an int for data.
        """
        self.assertRaises(
            TypeError,
            msr.read_meteor_summary_csv_as_dataframe,
            5,
            csv_data_directory_format=True,
        )

    def test_read_meteor_summary_csv_as_dataframe_rest_api(self) -> None:
        """
        Test: That a trajectory summary buffer can be read as a dataframe by checking
         properties.
        When: read_meteor_summary_csv_as_dataframe is called.
        """
        self._test_read_meteor_summary_using_data_frame(
            msr.read_meteor_summary_csv_as_dataframe(
                open(self.test_rest_api_file_path).read(),
                csv_data_directory_format=False,
            )
        )

    def test_read_meteor_summary_csv_as_numpy_array(self) -> None:
        """
        Test: That the trajectory summary buffer can be read as a numpy array by
         checking properties.
        When: read_meteor_summary_csv_as_numpy_array is called.
        """
        self._test_read_trajectory_summary_using_numpy_array(
            msr.read_meteor_summary_csv_as_numpy_array(
                self.test_data_directory_file_path1, csv_data_directory_format=True
            )
        )

    def test_read_trajectory_summary_file_as_data_frame(self) -> None:
        """
        Test: That the trajectory summary file can be read as a dataframe by
         checking properties.
        When: read_meteor_summary_csv_as_dataframe is called with a file path.
        """
        self._test_read_trajectory_summary_using_data_frame(
            msr.read_meteor_summary_csv_as_dataframe(
                self.test_data_directory_file_path1, csv_data_directory_format=True
            )
        )

    def test_read_trajectory_summary_file_as_data_frame_camel_case(self) -> None:
        """
        Test: That the trajectory summary file can be read as a dataframe by
         checking properties with camel case column names.
        When: read_meteor_summary_csv_as_dataframe is called with camel case
         option.
        """
        actual = msr.read_meteor_summary_csv_as_dataframe(
            self.test_data_directory_file_path1,
            camel_case_column_names=True,
            csv_data_directory_format=True,
        )
        self.assertEqual(
            actual.columns.tolist(),
            EXPECTED_COLUMN_NAMES_CAMEL_CASE,
        )

    def test_read_trajectory_summary_file_as_data_frame_avro_compatible(self) -> None:
        """
        Test: That the trajectory summary dataframe can be converted to avro format and
         abide by the schema.
        When: read_meteor_summary_csv_as_dataframe is called with avro_compatible
         option.
        """
        data_frame = msr.read_meteor_summary_csv_as_dataframe(
            self.test_data_directory_file_path1,
            avro_compatible=True,
            csv_data_directory_format=True,
        )
        actual_rows = data_frame.to_dict(orient="records")

        schema = Schema(json.dumps(get_meteor_summary_avro_schema()))
        parsed_schema = schema.parse()

        for row in actual_rows:
            self.assertTrue(parsed_schema.validate(row))

    def test_read_meteor_summary_csv_as_numpy_array_file(self) -> None:
        """
        Test: That the trajectory summary file can be read as a numpy array by checking
         properties.
        When: read_meteor_summary_csv_as_numpy_array is called.
        """
        self._test_read_trajectory_summary_using_numpy_array(
            msr.read_meteor_summary_csv_as_numpy_array(
                self.test_data_directory_file_path1, csv_data_directory_format=True
            )
        )

    def _test_read_trajectory_summary_using_data_frame(
        self, actual_dataframe: pd.DataFrame
    ) -> None:
        """
        Asserts properties about the data directory trajectory dataframe.

        :param actual_dataframe: The dataframe to test.
        """
        self.assertEqual(False, actual_dataframe.empty)
        self.assertEqual((534, 86), actual_dataframe.shape)
        self.assertEqual(
            ["20220304220741_yrPTs", "20220304221458_vpeSU", "20220304221734_ii908"],
            actual_dataframe.index.tolist()[:3],
        )
        self.assertEqual(EXPECTED_DTYPES, actual_dataframe.dtypes.tolist())
        self.assertEqual(EXPECTED_COLUMN_NAMES, actual_dataframe.columns.tolist())
        self.assertEqual("Unique trajectory (identifier)", actual_dataframe.index.name)

    def _test_read_meteor_summary_using_data_frame(
        self, actual_dataframe: pd.DataFrame
    ) -> None:
        """
        Asserts properties about the rest api meteor summary dataframe.

        :param actual_dataframe: The dataframe to test.
        """
        self.assertEqual(False, actual_dataframe.empty)
        self.assertEqual((100, 86), actual_dataframe.shape)
        self.assertEqual(
            ["20220304220741_yrPTs", "20220401012310_f5I2M", "20220401012318_BIAD6"],
            actual_dataframe.index.tolist()[:3],
        )
        actual_dataframe.info()
        self.assertEqual(EXPECTED_DTYPES, actual_dataframe.dtypes.tolist())
        self.assertEqual(EXPECTED_COLUMN_NAMES, actual_dataframe.columns.tolist())
        self.assertEqual("Unique trajectory (identifier)", actual_dataframe.index.name)

    def _test_read_trajectory_summary_using_numpy_array(
        self, actual_numpy_array: npt.NDArray[Any]
    ) -> None:
        """
        Asserts properties about the numpy array.

        :param actual_numpy_array: The numpy array to test.
        """
        self.assertEqual((534, 86), actual_numpy_array.shape)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
