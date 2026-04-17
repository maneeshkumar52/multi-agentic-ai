import re
from urllib.parse import urlparse
from utils import Logger

class ComplianceGuardAgent:
    def __init__(self):
        self.logger = Logger("ComplianceGuardAgent")

    def validate(self, search_result):
        """Validate search results for compliance and quality"""
        try:
            self.logger.log_agent_activity("ComplianceGuardAgent", "Starting validation")

            if not search_result or search_result.get('status') != 'success':
                return {
                    'status': 'rejected',
                    'approved': False,
                    'cleaned_results': [],
                    'validated_summary': None,
                    'original_count': 0,
                    'cleaned_count': 0,
                    'issues': ['Invalid search result input'],
                    'quality_score': 0.0
                }

            results = search_result.get('results', [])
            original_count = len(results)

            # Step 1: Validate citations and basic structure
            cleaned_results = self._validate_citations(results)

            # Step 2: Remove duplicates
            cleaned_results = self._remove_duplicates(cleaned_results)

            # Step 3: Validate AI summary
            validated_summary = self._validate_ai_summary(search_result.get('ai_summary'), cleaned_results)

            # Step 4: Check content quality
            quality_score = self._check_content_quality(cleaned_results)

            cleaned_count = len(cleaned_results)

            # Determine approval
            issues = []

            if cleaned_count == 0:
                issues.append('No valid results after validation')
                quality_score = 0.0

            if cleaned_count < original_count * 0.5:  # Less than 50% results remain
                issues.append(f'Too many results filtered: {original_count - cleaned_count} removed')

            if quality_score < 0.3:  # Minimum quality threshold
                issues.append(f'Quality score too low: {quality_score:.2f}')

            # Check for minimum requirements
            min_results = 2
            if cleaned_count < min_results:
                issues.append(f'Insufficient valid results: {cleaned_count} < {min_results}')

            approved = len(issues) == 0

            result = {
                'status': 'approved' if approved else 'rejected',
                'approved': approved,
                'cleaned_results': cleaned_results,
                'validated_summary': validated_summary,
                'original_count': original_count,
                'cleaned_count': cleaned_count,
                'issues': issues,
                'quality_score': quality_score
            }

            self.logger.log_agent_activity("ComplianceGuardAgent",
                f"Validation complete: {'approved' if approved else 'rejected'} "
                f"({cleaned_count}/{original_count} results, score: {quality_score:.2f})")

            return result

        except Exception as e:
            self.logger.log_error(f"Validation failed: {e}")
            return {
                'status': 'rejected',
                'approved': False,
                'cleaned_results': [],
                'validated_summary': None,
                'original_count': 0,
                'cleaned_count': 0,
                'issues': [f'Validation error: {str(e)}'],
                'quality_score': 0.0
            }

    def _validate_citations(self, results):
        """Validate that each result has proper citations and structure"""
        cleaned = []

        for result in results:
            try:
                # Check required fields
                if not all(key in result for key in ['title', 'url', 'snippet', 'source']):
                    continue

                title = result['title'].strip()
                url = result['url'].strip()
                snippet = result['snippet'].strip()
                source = result['source']

                # Validate field content
                if not title or len(title) < 3:
                    continue

                if not url or not self._is_valid_url(url):
                    continue

                if not snippet or len(snippet) < 10:
                    continue

                if source != 'DuckDuckGo':
                    continue

                cleaned.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet,
                    'source': source
                })

            except Exception as e:
                self.logger.log_error(f"Error validating result: {e}")
                continue

        return cleaned

    def _remove_duplicates(self, results):
        """Remove duplicate results based on URL"""
        seen_urls = set()
        cleaned = []

        for result in results:
            url = result['url']
            if url not in seen_urls:
                seen_urls.add(url)
                cleaned.append(result)

        return cleaned

    def _validate_ai_summary(self, summary, results):
        """Validate AI summary against actual results"""
        if not summary:
            return None

        if not results:
            return None

        try:
            # Check if summary is too generic
            generic_phrases = [
                'based on the search results',
                'the search results show',
                'according to the sources',
                'the information provided'
            ]

            summary_lower = summary.lower()
            if any(phrase in summary_lower for phrase in generic_phrases):
                # Check if it actually references specific content
                result_titles = [r['title'].lower() for r in results]
                result_snippets = [r['snippet'].lower() for r in results]

                has_specific_reference = False
                for title in result_titles:
                    if title.split()[0] in summary_lower:  # Check first word of title
                        has_specific_reference = True
                        break

                if not has_specific_reference:
                    for snippet in result_snippets:
                        if any(word in summary_lower for word in snippet.split()[:3]):  # First 3 words
                            has_specific_reference = True
                            break

                if not has_specific_reference:
                    return None  # Generic summary without specific references

            return summary

        except Exception as e:
            self.logger.log_error(f"AI summary validation error: {e}")
            return None

    def _check_content_quality(self, results):
        """Calculate content quality score"""
        if not results:
            return 0.0

        total_score = 0.0

        for result in results:
            score = 0.0

            # Title quality (0-0.3)
            title = result['title']
            if len(title) > 10 and not title.isupper():  # Not all caps spam
                score += 0.3

            # URL quality (0-0.3)
            url = result['url']
            if self._is_valid_url(url):
                # Prefer HTTPS
                if url.startswith('https://'):
                    score += 0.3
                else:
                    score += 0.2

            # Snippet quality (0-0.4)
            snippet = result['snippet']
            if len(snippet) > 50:
                score += 0.4
            elif len(snippet) > 20:
                score += 0.2

            total_score += score

        # Average score across all results
        avg_score = total_score / len(results)

        # Normalize to 0-1 scale
        return min(avg_score, 1.0)

    def _is_valid_url(self, url):
        """Check if URL is valid"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False