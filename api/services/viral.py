import logging
from typing import List, Optional, Dict
import json
import re
from services.gemini_utils import gemini_service

logger = logging.getLogger(__name__)

class ViralAnalysisService:
    """
    Service untuk menganalisis potensi viral konten dengan analisis dinamis dari Gemini.
    """
    
    def __init__(self):
        pass

    async def _get_dynamic_engaging_words(self, category: str, content_snippet: str) -> List[str]:
        """Secara dinamis mendapatkan daftar kata-kata yang menarik dari Gemini."""
        prompt = f"""
        Act as a YouTube growth hacking expert. Based on the content category "{category}" and the following snippet, generate a JSON list of 10-15 highly engaging, "viral" keywords and phrases commonly used in successful YouTube titles for this niche.
        Focus on words that create curiosity, urgency, or promise strong value.

        Content Snippet:
        ---
        {content_snippet[:1000]}
        ---

        Provide your response ONLY as a valid JSON object with a single key "engaging_words" containing a list of strings.
        Example: {{"engaging_words": ["secret revealed", "life hack", "must-watch"]}}

        JSON Response:
        """
        try:
            response_text = await gemini_service._generate_content(prompt)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.error("Gemini did not return a valid JSON object for engaging words.")
                return []
            clean_json = json_match.group(0)
            words_data = json.loads(clean_json)
            engaging_words = words_data.get("engaging_words", [])
            if isinstance(engaging_words, list) and all(isinstance(w, str) for w in engaging_words):
                logger.info(f"Dynamically generated engaging words for category '{category}': {engaging_words}")
                return [word.lower() for word in engaging_words]
            return []
        except Exception as e:
            logger.error(f"Failed to get dynamic engaging words from Gemini: {e}")
            return ['how to', 'why', 'secret', 'amazing', 'guide', 'ultimate', 'best', 'worst', 'shocking', 'hack', 'tips', 'tricks']

    def _detect_category(self, title: str, content: str) -> str:
        """Mendeteksi kategori konten."""
        text_to_scan = (title + " " + content).lower()
        categories: Dict[str, List[str]] = {
            "tech": ["ai", "programming", "software", "gadget", "review"],
            "business": ["marketing", "startup", "finance", "investment", "strategy"],
            "tutorial": ["how to", "guide", "step-by-step", "tutorial", "learn"],
            "entertainment": ["comedy", "vlog", "challenge", "reaction"],
            "education": ["science", "history", "explained", "documentary"],
        }
        for category, keywords in categories.items():
            if any(keyword in text_to_scan for keyword in keywords):
                return category
        return "general"

    async def calculate_viral_score(self, content: str, title: str, views: int, likes: int, comments: List[str]) -> int:
        """Menghitung skor potensi viral."""
        try:
            logger.info("Calculating dynamic viral score...")
            score = 0
            content_lower = content.lower()
            title_lower = title.lower()
            category = self._detect_category(title_lower, content_lower)
            logger.info(f"Detected content category: {category}")
            engaging_words = await self._get_dynamic_engaging_words(category, content)
            title_score = sum(8 for word in engaging_words if word in title_lower)
            score += min(title_score, 20)
            if views > 1000:
                engagement_ratio = (likes / views) if likes > 0 else 0
                if engagement_ratio > 0.05: score += 25
                elif engagement_ratio > 0.03: score += 20
                elif engagement_ratio > 0.015: score += 15
                else: score += 10
            else:
                score += 10
            score += 5 
            quality_and_trends = ['tutorial', 'guide', 'review', 'comparison', 'case study', 'explained', 'documentary', 'ai', 'productivity', 'health', 'finance']
            quality_score = sum(3 for indicator in quality_and_trends if indicator in content_lower)
            score += min(quality_score, 20)
            content_length = len(content.split())
            if 150 <= content_length <= 700: score += 10
            else: score += 5
            final_score = max(0, min(100, score))
            logger.info(f"Dynamic viral score calculated. Category: {category}, Final Score: {final_score}")
            return final_score
        except Exception as e:
            logger.error(f"Error calculating dynamic viral score: {str(e)}", exc_info=True)
            return 70