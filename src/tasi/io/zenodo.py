import logging
from enum import Enum
from typing import Dict, Optional

import requests


class ZenodoConnector:
    """
    A class to interact with the Zenodo API and retrieve information.
    This class queries Zenodo records based on a given title, extracts version
    and DOI information, and generates an Enum for the dataset versions.
    """

    ZENODO_API: str = "https://zenodo.org/api/records"

    def __init__(self, title: str, parent_id: int | None = None):
        """
        Initializes the ZenodoConnector object with a given title.

        Args:
            title (str): The title of the dataset to query from Zenodo.
            parent_id (int, optional): The index of the parent record.
        """
        self.title = title
        self.parent_id = parent_id

        self.records = self.get_records()
        self.versions = self.get_versions()
        self.dois = self.get_dois()

    def get_records(self) -> list[Dict]:
        """
        This method sends a GET request to the Zenodo API and retrieves all
        records matching the given title. The records are then sorted by
        their creation date.

        Returns:
            list[Dict]: A list of records from Zenodo, sorted by creation date.

        Raises:
            requests.exceptions.RequestException: If there is an error with the HTTP request.
            ValueError: If no records are found for the given title.
        """
        # define query parameters
        params = {
            "q": f'metadata.title:"{self.title}"',
            "all_versions": True,
            "sort": "mostrecent",
        }

        # ensure the records have the requested parent record
        if self.parent_id is not None:
            params["custom"] = f'pid_value:"{self.parent_id}"'

        try:
            # query API
            response = requests.get(self.ZENODO_API, params=params)

            if response.status_code == 200:
                # Extract records from response
                records = response.json()["hits"]["hits"]

                if not records:
                    raise ValueError(
                        f"No records found for {self.title=} and {self.parent_id=}"
                    )

                return records
            else:
                raise requests.exceptions.RequestException(
                    f"Error retrieving data. Status code: {response.status_code}"
                )
        except requests.exceptions.ProxyError as err:
            logging.warning(
                "Failed to fetch datasets because of a proxy connection error. "
                + "Ensure that the proxy is properly configured and allows accessing zenodo.org"
            )
            return []

    def get_versions(self) -> Dict[str, int]:
        """
        This method extracts the version information from each record and
        returns it as a dictionary, along with the latest version.

        Returns:
            Dict[str, int]: A dictionary of versions with 'v' prefixed and
                            version numbers as keys, including the latest version.
        """
        # Get the latest version
        if self.records:

            latest_version = {"latest": "v" + self.records[0]["metadata"]["version"]}

            # Get all other versions
            versions = {
                "v"
                + record["metadata"]["version"].replace(".", "_"): "v"
                + record["metadata"]["version"]
                for record in self.records
            }

            # Return all versions
            return {**latest_version, **versions}

        return {}

    def get_dois(self) -> Dict[str, int]:
        """
        This method extracts the DOI information from each record and maps
        it to its respective version. It also returns the latest DOI.

        Returns:
            Dict[str, int]: A dictionary of DOIs with 'v' prefixed and version
                            numbers as keys, including the latest DOI.
        """
        if self.records:

            # Get the latest DOI
            latest_doi = {"latest": int(self.records[0]["doi"].split(".")[-1])}

            # Get all other DOIs
            dois = {
                "v" + record["metadata"]["version"]: int(record["doi"].split(".")[-1])
                for record in self.records
            }

            # Return all DOIs
            return {**latest_doi, **dois}

        return {}

    def get_version_enum(self) -> Optional[Enum]:
        """
        Generates an Enum for the versions.

        This method generates an Enum class for the dataset versions, using
        the version data extracted from the records.

        Returns:
            Enum: An Enum class representing the dataset versions.
        """
        if self.versions:
            return Enum(self.title.replace(" ", "") + "Version", self.versions)
