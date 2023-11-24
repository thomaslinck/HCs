"""
main module for ForumClient
"""

import os
import json
import asyncio

from forum_client import ForumClient, LOsTreeRequest, HCRequest

FORUM_BASE_URL = "https://forum.minerva.edu/api/v1/"
FORUM_COOKIES_ENV_VAR = "FORUM_COOKIES"


def build_forum_client() -> ForumClient:
    """
    Initializes and returns a ForumClient object.

    This function loads the environment variables using `load_dotenv()` to ensure that the required variables are available. It then creates a new instance of the `ForumClient` class, passing the `FORUM_BASE_URL` and `FORUM_COOKIES_ENV_VAR` as parameters. The value of `FORUM_COOKIES_ENV_VAR` is obtained from the environment using `os.getenv()`.

    Returns:
        A `ForumClient` object that can be used to interact with the forum API.
    """
    return ForumClient(FORUM_BASE_URL, os.getenv(FORUM_COOKIES_ENV_VAR, ""))


def extract_HCs_from_LOs(stack: list) -> dict:
    """

    Args:
        stack (list): A list representing the LOsTree.

    Returns:
        list: A list of extracted HCs as dictionaries.
    """
    HCs = {}
    while stack:
        current = stack.pop()

        if "hc-group-nodes" in current.keys():
            stack.extend(current["hc-group-nodes"])

        if "hc-leaf-nodes" in current.keys():
            for hc in current["hc-leaf-nodes"]:
                HCs[hc["hc-item"]["id"]] = hc["hc-item"]["hashtag"]
    return HCs


async def main():
    """
    Initializes the main function.
    """
    client = build_forum_client()

    LOTreeTask = asyncio.create_task(LOsTreeRequest(client).query())
    LOsTree = await LOTreeTask

    hcs = extract_HCs_from_LOs(LOsTree["hc-group-nodes"])

    tasks = [
        asyncio.create_task(HCRequest(client, hc_id).query()) for hc_id in hcs.keys()
    ]
    responses = await asyncio.gather(*tasks)

    with open("results/raw-results.json", "w") as file:
        json.dump(responses, file)

    processed_results = [
        {
            "id": list(hcs.keys())[i],
            "hashtag": list(hcs.values())[i],
            "comment": entry["comment"],
            "assessment": "not available"
            if not entry["score"]
            else "exceeds"
            if float(entry["score"]) >= 4
            else "improve",
            "type": entry["type"],
            "weight": entry["weight"],
        }
        for i, response in enumerate(responses)
        for entry in response
    ]

    with open("results/results-without-scores.json", "w") as file:
        json.dump(processed_results, file)


if __name__ == "__main__":
    asyncio.run(main())
