import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("FIRECRAWL_API_KEY")


if not api_key:
    raise ValueError("FIRECRAWL_API_KEY가 .env 파일에 설정되지 않았습니다.")


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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return f"Error using tool. Status Code: {response.status_code}, Response: {response.text}"

    response_json = response.json()

    if response_json.get("success") is not True:
        return "Error using tool: API call was not successful."

    cleaned_chunks = []

    for result in response_json.get("data", {}).get("web", []):
        title = result.get("title", "No Title")
        url = result.get("url", "No URL")
        markdown = result.get("markdown", "")

        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }

        cleaned_chunks.append(cleaned_result)

    return cleaned_chunks
