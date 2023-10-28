import logging
from typing import Any, List

import requests
from requests import HTTPError

logger = logging.getLogger(__name__)


class OpenAlexUtilConfig:
    """Configuration for OpenAlexUtil

    Attributes:
        work_endpoint (str): Endpoint to get a specific artifact using OpenAlexID.
        search_endpoint (str): Endpoint to search for artifacts using a query.
        filter_endpoint (str): Endpoint to filter artifacts.
    """

    def __init__(
        self,
        work_endpoint: str = "https://api.openalex.org/works/{}",
        search_endpoint: str = "https://api.openalex.org/works?search={}&filter=open_access.is_oa:true&per-page={}",
        filter_endpoint: str = "https://api.openalex.org/works?filter=",
    ) -> None:
        """Initializes KnowledgeGraphConfig

        Usage example:
        >>>oa_config = OpenAlexUtilConfig(work_endpoint="sample-url", search_endpoint="sample-url", filter_endpoint="sample-url")

        Args:
            work_endpoint (str): Endpoint to get a specific artifact using OpenAlexID.
            search_endpoint (str): Endpoint to search for artifacts using a query.
            filter_endpoint (str): Endpoint to filter artifacts.

        Returns:
            None: Initializes OpenAlexUtilConfig
        """
        self.work_endpoint = work_endpoint
        self.search_endpoint = search_endpoint
        self.filter_endpoint = filter_endpoint


class OpenAlexUtil:
    """Provides functionality to fetch artifacts from OpenAlex."""

    def __init__(self, config: OpenAlexUtilConfig = OpenAlexUtilConfig()) -> None:
        self.config = config or OpenAlexUtilConfig()

    def search_works(self, search_query: str, results_limit: int = 25) -> List[Any]:
        """Searches for artifacts using a query.

        Usage example:
        >>>oa_util = OpenAlexUtil()
        >>>oa_util.search_works("sample-query", 25)

        Args:
            search_query (str): Query to search for artifacts.
            results_limit (int): Number of results to return.

        Returns:
            List[ResearchArtifact]: List of artifacts that match the query.

        Raises:
            HTTPError: If an HTTP error occurs while searching for artifacts.
            Exception: If an error occurs while searching for artifacts.
        """
        url = self.config.search_endpoint.format(search_query, results_limit)

        try:
            response = requests.get(url)
            response.raise_for_status()
            search_results = response.json().get("results")
            if response.status_code == 200 and search_results is not None:
                return search_results
                # artifacts = [ResearchArtifact.parse_obj(_) for _ in search_results]
                # full_text_artifacts = list(map(lambda x: x.get_full_text(), artifacts))
                # return full_text_artifacts
            else:
                return []
        except HTTPError as http_err:
            logger.info(f"HTTP error occurred: {http_err}")
            return []
        except Exception as err:
            logger.info(f"Other error occurred: {err}")
            return []
