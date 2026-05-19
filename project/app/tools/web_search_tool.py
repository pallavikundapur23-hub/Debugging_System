import httpx
from typing import List

class WebSearchTool:
    SEARCH_URL = "https://duckduckgo.com/html/"

    async def search(self, query: str, limit: int = 3) -> List[str]:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.post(self.SEARCH_URL, data={"q": query})
            response.raise_for_status()
            html = response.text
            results = []
            for split in html.split("<a class=\"result__a\"")[:limit+1]:
                if "href=" in split:
                    href = split.split("href=")[1].split(">", 1)[0].strip('"')
                    if href.startswith("http"):
                        results.append(href)
                if len(results) >= limit:
                    break
            return results
