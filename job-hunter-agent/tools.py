import os
import re

import requests


def web_search_tool(query: str) -> str:
    """
    Search the web for information.
    """
    url = "https://api.firecrawl.dev/v2/search"

    payload = {
        "query": query,
        "sources": ["web"],
        "categories": [],
        "limit": 10,
        "scrapeOptions": {
            "onlyMainContent": True,
            "maxAge": 172800000,
            "parsers": ["pdf"],
            "formats": ["markdown"],
        },
    }

    headers = {
        "Authorization": "Bearer fc-611d3767924a4d689ef974262ec35ec3",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    response = response.json()

    if response["success"] is not True:
        return "Error using tool."

    cleaned_chunks = []

    for result in response["data"]["web"]:
        title = result["title"]
        url = result["url"]
        markdown = result["markdown"] if "markdown" in result else ""

        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }

        cleaned_chunks.append(cleaned_result)

    return cleaned_chunks


print(web_search_tool("remote jobs in korea"))
