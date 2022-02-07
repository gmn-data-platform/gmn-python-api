"""
This module contains functions to read trajectory summary files from the GMN
data directory.
"""
from datetime import datetime
from typing import List
from typing import Optional

import requests
from bs4 import BeautifulSoup  # type: ignore

# The base URL for trajectory summary files in the GMN data directory
BASE_URL: str = "https://globalmeteornetwork.org/data/traj_summary_data/"

# The date of the earliest trajectory summary file in the GMN data directory
DATA_START_DATE: datetime = datetime(2018, 1, 9)

# The name of the directory containing daily trajectory summary files in the
# base URL.
DAILY_DIRECTORY: str = "daily/"

# The name of the directory containing monthly trajectory summary files in
# the base URL.
MONTHLY_DIRECTORY: str = "monthly/"

# The extension of the trajectory summary files in the GMN data directory
SUMMARY_FILE_EXTENSION: str = "txt"

# The filename of the most recent trajectory summary file
SUMMARY_TODAY_FILENAME: str = "traj_summary_latest_daily.txt"

# The filename of the trajectory summary file from yesterday
SUMMARY_YESTERDAY_FILENAME: str = "traj_summary_yesterday.txt"


def get_all_daily_file_urls() -> List[str]:
    """
    Get all daily trajectory summary file urls from the GMN data directory.
    :return: (List[str]) A list of all daily file urls.
    :raises: (requests.HTTPError) If the data directory url doesn't return a
    200 response.
    """
    return _get_url_paths(BASE_URL + DAILY_DIRECTORY, SUMMARY_FILE_EXTENSION)


def get_all_monthly_file_urls() -> List[str]:
    """
    Get all monthly trajectory summary file urls from the GMN data directory.
    :return: (List[str]) A list of all monthly file urls.
    :raises: (requests.HTTPError) If the data directory url doesn't return a
    200 response.
    """
    return _get_url_paths(BASE_URL + MONTHLY_DIRECTORY, SUMMARY_FILE_EXTENSION)


def get_daily_file_url_by_date(
    date: datetime, current_date: Optional[datetime] = None
) -> str:
    """
    Get the URL of the daily trajectory summary file for a given date.
    :param date: (datetime) The date of the daily file.
    :param current_date: (Optional datetime) The current date. Defaults to
    datetime.now().
    :return: (str) The URL of the daily file.
    :raises: (requests.HTTPError) If the data directory url doesn't return a
    200 response.
    """
    if not current_date:
        current_date = datetime.today()

    if date == current_date:
        return BASE_URL + DAILY_DIRECTORY + SUMMARY_TODAY_FILENAME

    if date.day == current_date.day - 1:
        return BASE_URL + DAILY_DIRECTORY + SUMMARY_YESTERDAY_FILENAME

    all_daily_filenames = get_all_daily_file_urls()
    files_containing_date = [
        f for f in all_daily_filenames if date.strftime("%Y%m%d") in f
    ]
    return files_containing_date[0]


def get_monthly_file_url_by_month(date: datetime) -> str:
    """
    Get the URL of the monthly trajectory summary file for a given month.
    :param date: (datetime) The date of the monthly file.
    :return: (str) The URL of the monthly file.
    :raises: (requests.HTTPError) If the data directory url doesn't return a
    200 response.
    """
    all_monthly_filenames = get_all_monthly_file_urls()
    files_containing_date = [
        f for f in all_monthly_filenames if date.strftime("%Y%m") in f
    ]
    return files_containing_date[0]


def get_daily_file_content_by_date(
    date: datetime, current_date: Optional[datetime] = None
) -> str:
    """
    Get the content of the daily trajectory summary file for a given date.
    :param date: (datetime) The date of the daily file.
    :param current_date: (Optional datetime) The current date. Defaults to
    datetime.now().
    :return: (str) The content of the daily file.
    :raises: (requests.HTTPError) If the data directory url doesn't return a
    200 response.
    """
    file_url = get_daily_file_url_by_date(date, current_date)

    response = requests.get(file_url)
    if response.ok:
        return str(response.text)
    else:
        response.raise_for_status()
        return ""  # pragma: no cover


def get_monthly_file_content_by_date(date: datetime) -> str:
    """
    Get the content of the monthly trajectory summary file for a given date.
    :param date: (datetime) The date to get the monthly file for.
    :return: (str) The content of the monthly file.
    :raises: (requests.HTTPError) If the data directory url doesn't return a
    200 response.
    """
    file_url = get_monthly_file_url_by_month(date)

    response = requests.get(file_url)
    if response.ok:
        return str(response.text)
    else:
        response.raise_for_status()
        return ""  # pragma: no cover


def _get_url_paths(url: str, ext: str = "") -> List[str]:
    """
    Get all paths from a directory listing URL.
    :param url: (str) The URL to get the paths from.
    :param ext: (Optional str) The extension to filter by.
    :return: (List[str]) A list of all paths.
    :raises: (requests.HTTPError) If the URL doesn't return a 200 response.
    """
    response = requests.get(url)
    if response.ok:
        response_text = str(response.text)
    else:
        response.raise_for_status()
        return []  # pragma: no cover
    soup = BeautifulSoup(response_text, "html.parser")
    parent = [
        url + node.get("href")
        for node in soup.find_all("a")
        if node.get("href").endswith(ext)
    ]
    return parent
