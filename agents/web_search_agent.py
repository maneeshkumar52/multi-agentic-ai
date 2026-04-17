import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from utils import Config, Logger

# Import Azure OpenAI with try/except
try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

class WebSearchAgent:
    def __init__(self):
        self.logger = Logger("WebSearchAgent")

        # Initialize Azure OpenAI client
        self.azure_client = None
        if AZURE_OPENAI_AVAILABLE:
            try:
                self.azure_client = AzureOpenAI(
                    api_version=Config.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                    api_key=Config.AZURE_OPENAI_API_KEY
                )
                self.logger.log_agent_activity("WebSearchAgent", "Azure OpenAI client initialized")
            except Exception as e:
                self.logger.log_error(f"Failed to initialize Azure OpenAI client: {e}")
                self.azure_client = None
        else:
            self.logger.log_agent_activity("WebSearchAgent", "Azure OpenAI not available")

    def search(self, query, num_results=5):
        """Search DuckDuckGo and return structured results with AI summary"""
        try:
            self.logger.log_agent_activity("WebSearchAgent", f"Starting search for: {query}")

            # Scrape DuckDuckGo HTML
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract results
            results = []
            result_divs = soup.find_all('div', class_='result')

            for div in result_divs[:num_results]:
                try:
                    # Extract title
                    title_elem = div.find('a', class_='result__a')
                    title = title_elem.get_text().strip() if title_elem else "No title"

                    # Extract URL - handle DuckDuckGo redirect
                    url = ""
                    if title_elem and 'href' in title_elem.attrs:
                        href = title_elem['href']
                        if 'uddg=' in href:
                            # Parse the redirect URL
                            from urllib.parse import urlparse, parse_qs
                            parsed = urlparse(href)
                            query = parse_qs(parsed.query)
                            if 'uddg' in query:
                                url = query['uddg'][0]
                        else:
                            url = href

                    # Extract snippet from result__body
                    snippet = ""
                    body_elem = div.find('div', class_='result__body')
                    if body_elem:
                        # Remove the title and URL parts to get just the snippet
                        text_parts = []
                        for elem in body_elem.find_all(text=True, recursive=True):
                            text = elem.strip()
                            if text and len(text) > 10 and text not in title:
                                text_parts.append(text)
                        snippet = ' '.join(text_parts).strip()
                        # Limit snippet length
                        if len(snippet) > 300:
                            snippet = snippet[:300] + "..."

                    if title and url and snippet:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': 'DuckDuckGo'
                        })

                except Exception as e:
                    self.logger.log_error(f"Error parsing result: {e}")
                    continue

            # Generate AI summary
            ai_summary = self._generate_ai_summary(query, results)

            # Prepare response
            sources = [r['url'] for r in results if r['url']]

            response_data = {
                'status': 'success',
                'query': query,
                'results': results,
                'total_results': len(results),
                'sources': sources,
                'ai_summary': ai_summary
            }

            self.logger.log_agent_activity("WebSearchAgent", f"Search completed: {len(results)} results found")
            return response_data

        except Exception as e:
            self.logger.log_error(f"Search failed: {e}")
            return {
                'status': 'error',
                'query': query,
                'results': [],
                'total_results': 0,
                'sources': [],
                'ai_summary': None,
                'error': str(e)
            }

    def _generate_ai_summary(self, query, results):
        """Generate AI summary using Azure OpenAI"""
        if not self.azure_client or not results:
            return None

        try:
            # Prepare results text for AI
            results_text = "\n".join([
                f"- {r['title']}: {r['snippet'][:200]}..."
                for r in results[:3]  # Limit to first 3 results for summary
            ])

            system_prompt = "You are a helpful research assistant. Summarize the key findings from these search results in 2-3 sentences."
            user_prompt = f"Query: {query}\n\nSearch Results:\n{results_text}\n\nSummary:"

            response = self.azure_client.chat.completions.create(
                model=Config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )

            summary = response.choices[0].message.content.strip()
            self.logger.log_agent_activity("WebSearchAgent", "AI summary generated successfully")
            return summary

        except Exception as e:
            self.logger.log_error(f"AI summary generation failed: {e}")
            return None