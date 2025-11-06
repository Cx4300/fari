"""
FARADAY AI - Web Search Tool
"""

import asyncio
from typing import List, Dict, Any
import aiohttp
from urllib.parse import quote_plus

from tools.function_registry import register_function
from config.settings import settings
from utils.logger import logger


@register_function(
    name="web_search",
    description="Search the web for current information. Use this when you need up-to-date information, news, or facts that might not be in your training data.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }
)
async def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the web for information.

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        Search results with titles, snippets, and URLs
    """
    try:
        logger.info(f"🔍 Web search: {query}")

        # Check if web search is enabled
        if not settings.is_tool_enabled("web_search"):
            logger.warning("⚠️  Web search is disabled")
            return {
                "success": False,
                "error": "Web search is disabled in settings"
            }

        api_key = settings.tools.web_search_api_key
        engine = settings.tools.web_search_engine

        if engine == "google" and api_key:
            results = await _google_search(query, num_results, api_key)
        elif engine == "bing" and api_key:
            results = await _bing_search(query, num_results, api_key)
        elif engine == "duckduckgo":
            results = await _duckduckgo_search(query, num_results)
        else:
            # Fallback: simulated search
            logger.warning("⚠️  No valid search engine configured, using fallback")
            results = await _fallback_search(query, num_results)

        logger.info(f"✅ Found {len(results)} results")

        return {
            "success": True,
            "query": query,
            "results": results,
            "total_results": len(results)
        }

    except Exception as e:
        logger.error(f"❌ Web search error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def _google_search(query: str, num_results: int, api_key: str) -> List[Dict[str, str]]:
    """Search using Google Custom Search API"""
    # Note: Requires Google Custom Search API key and Search Engine ID
    # For demo purposes, this is a placeholder
    logger.info("Using Google search (placeholder)")
    return await _fallback_search(query, num_results)


async def _bing_search(query: str, num_results: int, api_key: str) -> List[Dict[str, str]]:
    """Search using Bing Search API"""
    try:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {
            "q": query,
            "count": num_results,
            "textDecorations": True,
            "textFormat": "HTML"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []

                    for item in data.get('webPages', {}).get('value', []):
                        results.append({
                            "title": item.get('name', ''),
                            "snippet": item.get('snippet', ''),
                            "url": item.get('url', ''),
                            "source": "Bing"
                        })

                    return results
                else:
                    logger.error(f"Bing search failed: {response.status}")
                    return await _fallback_search(query, num_results)

    except Exception as e:
        logger.error(f"Bing search error: {e}")
        return await _fallback_search(query, num_results)


async def _duckduckgo_search(query: str, num_results: int) -> List[Dict[str, str]]:
    """Search using DuckDuckGo (unofficial API)"""
    try:
        # DuckDuckGo Instant Answer API
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []

                    # Get abstract
                    if data.get('Abstract'):
                        results.append({
                            "title": data.get('Heading', query),
                            "snippet": data.get('Abstract', ''),
                            "url": data.get('AbstractURL', ''),
                            "source": "DuckDuckGo"
                        })

                    # Get related topics
                    for topic in data.get('RelatedTopics', [])[:num_results-1]:
                        if isinstance(topic, dict) and 'Text' in topic:
                            results.append({
                                "title": topic.get('Text', '').split(' - ')[0],
                                "snippet": topic.get('Text', ''),
                                "url": topic.get('FirstURL', ''),
                                "source": "DuckDuckGo"
                            })

                    return results[:num_results]
                else:
                    return await _fallback_search(query, num_results)

    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return await _fallback_search(query, num_results)


async def _fallback_search(query: str, num_results: int) -> List[Dict[str, str]]:
    """Fallback search (simulated results)"""
    logger.warning("⚠️  Using fallback search (simulated results)")

    # Simulate search results
    await asyncio.sleep(0.5)  # Simulate network delay

    return [
        {
            "title": f"Result {i+1} for '{query}'",
            "snippet": f"This is a simulated search result for the query: {query}. "
                      f"To use real web search, configure a search API key in settings.",
            "url": f"https://example.com/result{i+1}",
            "source": "Simulated"
        }
        for i in range(num_results)
    ]


# Export
__all__ = ['web_search']
