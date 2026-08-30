from tavily import TavilyClient

from config.api_keys import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str) -> str:
    """
    Performs a search using Tavily and returns a clean context string.
    """
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=5)

        context = ""
        for result in response["results"]:
            context += f"Source: {result['url']}\nContent: {result['content']}\n\n"

        return context if context else "No web results found."
    except Exception as e:
        print(f"Tavily Error: {e}")
        return "Web search failed."
