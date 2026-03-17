from duckduckgo_search import DDGS


def web_search_tool(query: str):
    """
    Web Search Tool.
    Args:
        query: str
            The query to search the web for.
    Returns
        A list of search results with the website content in Markdown format.
    """
    results = DDGS().text(query, max_results=5)

    cleaned_chunks = []

    for result in results:
        cleaned_chunks.append(
            {
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "markdown": result.get("body", ""),
            }
        )

    return cleaned_chunks
