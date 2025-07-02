import os
import logging
from typing import Dict, List
import google.generativeai as genai
from models.schemas import ContentRecommendation
import json

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini AI."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None
        else:
            logger.error("GEMINI_API_KEY not found. GeminiService cannot function.")
            self.model = None

    async def _generate_content(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content using Gemini API with error handling and retries."""
        if not self.model:
            raise Exception("Gemini model is not initialized. Please check your GEMINI_API_KEY.")

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,  # Lower temperature for more consistent results
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=2048,
                    ),
                    safety_settings=[
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "threshold": "BLOCK_NONE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "threshold": "BLOCK_NONE"
                        },
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "threshold": "BLOCK_NONE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_NONE"
                        }
                    ]
                )

                # Check if response has valid content
                if not response.candidates:
                    logger.warning(f"Attempt {attempt + 1}: No candidates returned from Gemini")
                    continue
                
                candidate = response.candidates[0]
                
                # Check finish reason
                if hasattr(candidate, 'finish_reason'):
                    if candidate.finish_reason == 2:  # SAFETY
                        logger.warning(f"Attempt {attempt + 1}: Content blocked by safety filters")
                        continue
                    elif candidate.finish_reason == 3:  # RECITATION
                        logger.warning(f"Attempt {attempt + 1}: Content blocked due to recitation")
                        continue
                    elif candidate.finish_reason != 1:  # Not STOP (successful completion)
                        logger.warning(f"Attempt {attempt + 1}: Unexpected finish reason: {candidate.finish_reason}")
                        continue

                # Try to get the text content
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    text_content = ""
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_content += part.text
                    
                    if text_content.strip():
                        return text_content.strip()
                
                # Fallback: try response.text if available
                if hasattr(response, 'text') and response.text:
                    return response.text.strip()
                
                logger.warning(f"Attempt {attempt + 1}: No valid text content found in response")
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Gemini API error: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to generate content from Gemini after {max_retries} attempts: {str(e)}")
                continue

        raise Exception("Failed to generate valid content from Gemini after all attempts")


gemini_service = GeminiService()

async def summarize_transcript(transcript_chunk: str) -> str:
    """
    Summarize a transcript chunk using Gemini AI.
    """
    if not transcript_chunk or len(transcript_chunk.strip()) < 10:
        return "No content available to summarize."

    # Clean and truncate the transcript to avoid issues
    clean_transcript = transcript_chunk.replace('\n', ' ').strip()[:3000]

    prompt = f"""
Please provide a comprehensive summary of the following content in 3-4 sentences.
Focus on the main topics, key insights, and important information.

Content: {clean_transcript}

Requirements:
- Write in clear, professional language
- Highlight the most important points
- Make it informative and easy to understand
- Focus on factual content only

Summary:
"""

    try:
        summary = await gemini_service._generate_content(prompt)
        return summary.strip()
    except Exception as e:
        logger.error(f"Error summarizing transcript: {e}")
        # Return a basic summary based on content length and keywords
        return _generate_fallback_summary(clean_transcript)

def _generate_fallback_summary(content: str) -> str:
    """Generate a basic summary when AI fails."""
    word_count = len(content.split())
    
    # Look for common keywords to determine content type
    keywords = {
        'tutorial': ['tutorial', 'how to', 'guide', 'step by step', 'learn'],
        'business': ['business', 'marketing', 'strategy', 'growth', 'revenue'],
        'technology': ['technology', 'software', 'programming', 'development', 'AI'],
        'education': ['education', 'course', 'lesson', 'teaching', 'study']
    }
    
    content_lower = content.lower()
    detected_type = 'general'
    
    for category, terms in keywords.items():
        if any(term in content_lower for term in terms):
            detected_type = category
            break
    
    return f"This {detected_type} content covers important topics and insights in approximately {word_count} words. The material provides valuable information that could be useful for learning and understanding key concepts in the subject area."

async def explain_why_viral(title: str, views: int, likes: int, summary: str) -> str:
    """
    Generate explanation for why content has viral potential.
    """
    # Clean inputs
    clean_title = title.replace('\n', ' ').strip()[:200]
    clean_summary = summary.replace('\n', ' ').strip()[:800]
    
    prompt = f"""
Analyze why this content has viral potential based on the information provided.

Title: {clean_title}
Views: {views:,}
Likes: {likes:,}
Content Summary: {clean_summary}

Provide a brief analysis covering:
1. What makes this content engaging
2. Why it resonates with audiences
3. Key viral factors

Keep the response factual and professional.

Analysis:
"""

    try:
        explanation = await gemini_service._generate_content(prompt)
        return explanation.strip()
    except Exception as e:
        logger.error(f"Error generating viral explanation: {e}")
        return _generate_fallback_viral_explanation(views, likes)

def _generate_fallback_viral_explanation(views: int, likes: int) -> str:
    """Generate fallback viral explanation."""
    engagement_ratio = (likes / views * 100) if views > 0 else 0
    
    if engagement_ratio > 5:
        return "This content shows strong viral potential due to its high engagement rate and compelling topic that resonates with viewers. The combination of valuable information and engaging presentation style makes it highly shareable."
    elif engagement_ratio > 2:
        return "This content demonstrates good viral potential with solid engagement metrics. The topic appears to be relevant and interesting to the target audience, with room for optimization in presentation and distribution."
    else:
        return "This content has moderate viral potential. While the topic may be valuable, improving the presentation style, timing, and audience targeting could significantly increase its viral reach and engagement."

async def generate_content_idea(category: str, summary: str, reason: str) -> ContentRecommendation:
    """
    Generate content recommendation based on analysis.
    """
    # Clean inputs
    clean_summary = summary.replace('\n', ' ').strip()[:600]
    clean_reason = reason.replace('\n', ' ').strip()[:600]
    
    prompt = f"""
Based on this content analysis, create a new content recommendation in JSON format.

Category: {category}
Original Summary: {clean_summary}
Success Factors: {clean_reason}

Create a JSON response with this exact structure:
{{
    "title": "Engaging title for new content",
    "target_audience": "Specific audience description",
    "content_style": "Recommended style and format",
    "suggested_structure": {{
        "hook": "Opening strategy",
        "introduction": "Introduction approach",
        "main_content": "Main content strategy",
        "call_to_action": "Engagement strategy"
    }},
    "pro_tips": [
        "Tip 1",
        "Tip 2", 
        "Tip 3",
        "Tip 4",
        "Tip 5"
    ],
    "estimated_viral_score": 75
}}

Respond only with valid JSON:
"""

    try:
        response_text = await gemini_service._generate_content(prompt)
        
        # Clean JSON response
        clean_json_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if clean_json_text.startswith('```json'):
            clean_json_text = clean_json_text[7:]
        if clean_json_text.startswith('```'):
            clean_json_text = clean_json_text[3:]
        if clean_json_text.endswith('```'):
            clean_json_text = clean_json_text[:-3]
        
        clean_json_text = clean_json_text.strip()
        
        # Parse JSON
        data = json.loads(clean_json_text)
        
        # Validate and create ContentRecommendation
        recommendation = ContentRecommendation(**data)
        return recommendation
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in content recommendation: {e}")
        logger.error(f"Raw response: {response_text[:500]}...")
        return _create_fallback_recommendation()
    except Exception as e:
        logger.error(f"Error generating content idea: {str(e)}")
        return _create_fallback_recommendation()

def _create_fallback_recommendation() -> ContentRecommendation:
    """Create a fallback recommendation when AI generation fails."""
    return ContentRecommendation(
        title="Create Engaging Content That Drives Results",
        target_audience="Content creators, entrepreneurs, and digital marketers aged 25-45",
        content_style="Educational tutorial with practical examples and clear step-by-step guidance",
        suggested_structure={
            "hook": "Start with a compelling question or surprising statistic that grabs attention",
            "introduction": "Briefly introduce the problem you're solving and the value you'll provide",
            "main_content": "Deliver actionable steps with real examples and visual demonstrations",
            "call_to_action": "Encourage viewers to try the technique and share their results"
        },
        pro_tips=[
            "Focus on solving a specific problem your audience faces daily",
            "Use clear, conversational language that's easy to follow",
            "Include visual elements and examples to maintain engagement",
            "Create content that viewers will want to save and share",
            "Optimize your title and thumbnail for maximum click-through rate"
        ],
        estimated_viral_score=78
    )

async def summarize_document(file_path: str) -> str:
    """
    Summarize document content.
    """
    logger.info(f"Summarizing document: {file_path}")

    # TODO: Implement actual document reading and processing
    # This would involve reading PDF, Word, or other document formats
    # and extracting text content for summarization

    mock_summary = f"""
    Document Analysis Summary:

    This document contains comprehensive information covering strategic planning,
    implementation guidelines, and industry best practices. Key themes include
    process optimization, stakeholder engagement, and measurable outcomes.

    The content provides actionable insights for professionals looking to improve
    their operational efficiency and strategic decision-making capabilities.
    """

    return await summarize_transcript(mock_summary)