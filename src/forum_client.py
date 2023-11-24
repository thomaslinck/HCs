"""
Module exports ForumClient
"""

from abc import ABC, abstractmethod
import aiohttp


class ForumClient:
    """
    Main client for forum
    """

    def __init__(self, base_url: str, cookies: str):
        self.base_url = base_url
        self.cookies = self.__parse_cookies(cookies)
        self.timeout = 1000

    def __parse_cookies(self, cookies_string: str) -> dict[str, str]:
        return {
            key.replace(" ", ""): value.replace(" ", "")
            for key, value in [
                cookie.split("=") for cookie in cookies_string.split(";")
            ]
        }

    async def query(self, relative_url: str):
        """
        Query a relative URL and write the response content to a JSON file.

        Args:
            relative_url (str): The relative URL to query.
            file_name (str): The name of the JSON file to write the response content to.

        Returns:
            None
        """
        url = self.base_url + relative_url
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url, cookies=self.cookies, timeout=self.timeout
                ) as response:
                    return await response.json()
            except Exception as e:
                print(f"Error fetching data from {url}: {e}")


class ForumRequest(ABC):
    """
    Base class for all requests
    """

    def __init__(self, forum_client: ForumClient):
        self.forum_client = forum_client

    async def query(self):
        """
        Query the forum client for data and write it to a JSON file.

        This function retrieves the relative URL and file name needed to perform the query
        from the respective methods of the class. It then calls the `query_and_write_to_json`
        method of the `forum_client` object, passing the relative URL and file name as arguments.

        Parameters:
            None

        Returns:
            None
        """
        return await self.forum_client.query(self.get_relative_url())

    @abstractmethod
    def get_relative_url(self) -> str:
        """
        Get the relative URL for the current instance.

        :return: A string representing the relative URL.
        :rtype: str
        """


class LOsTreeRequest(ForumRequest):
    """
    Queries all LOs from Forum
    Creates a file with all LOs and one with all HCs
    """

    def get_relative_url(self):
        return "hc-trees/current?tree"


class HCRequest(ForumRequest):
    """
    Queries all LOs from Forum
    Creates a file with all LOs and one with all HCs
    """

    def __init__(self, forum_client: ForumClient, hc_code: str):
        super().__init__(forum_client)
        self.hc_code = hc_code

    def get_relative_url(self):
        return f"outcomeindex/performance?hc-item={self.hc_code}"
