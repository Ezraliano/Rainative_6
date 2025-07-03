import os
import logging
import tempfile
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import PyPDF2
import docx
import pptx
from services.gemini_utils import gemini_service
import re

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """
    Service for analyzing documents and extracting key information.
    Focuses on summarization and important points extraction.
    """
    
    def __init__(self):
        self.max_content_length = 8000  # Limit content length for API calls
        self.min_content_length = 50    # Minimum content length for analysis
    
    async def analyze_document(self, file_path: str, file_extension: str, filename: str) -> Dict:
        """
        Main method to analyze a document and extract summary and key points.
        
        Args:
            file_path: Path to the uploaded file
            file_extension: File extension (.pdf, .docx, etc.)
            filename: Original filename
            
        Returns:
            Dictionary containing summary and key points
        """
        try:
            # Extract text content from document
            content = await self._extract_text_content(file_path, file_extension)
            
            if not content or len(content.strip()) < self.min_content_length:
                raise ValueError("Document content is too short or empty for analysis")
            
            # Clean and prepare content
            cleaned_content = self._clean_content(content)
            
            # Generate summary and key points
            summary = await self._generate_summary(cleaned_content, filename)
            key_points = await self._extract_key_points(cleaned_content, filename)
            
            # Analyze document structure and type
            doc_info = self._analyze_document_structure(cleaned_content, filename)
            
            return {
                "summary": summary,
                "key_points": key_points,
                "document_info": doc_info,
                "word_count": len(cleaned_content.split()),
                "content_preview": cleaned_content[:200] + "..." if len(cleaned_content) > 200 else cleaned_content
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise Exception(f"Failed to analyze document: {str(e)}")
    
    async def _extract_text_content(self, file_path: str, file_extension: str) -> str:
        """Extract text content from various document formats."""
        content = ""
        
        try:
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
            elif file_extension == '.pdf':
                content = await self._extract_pdf_content(file_path)
                
            elif file_extension in ['.doc', '.docx']:
                content = await self._extract_word_content(file_path)
                
            elif file_extension in ['.ppt', '.pptx']:
                content = await self._extract_powerpoint_content(file_path)
                
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting content from {file_extension}: {str(e)}")
            raise Exception(f"Failed to extract content from document: {str(e)}")
    
    async def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text from PDF files."""
        content = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            content += f"\n--- Page {page_num + 1} ---\n"
                            content += page_text
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                        continue
                        
            return content
            
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")
    
    async def _extract_word_content(self, file_path: str) -> str:
        """Extract text from Word documents."""
        content = ""
        try:
            doc = docx.Document(file_path)
            
            # Extract paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content += paragraph.text + "\n"
            
            # Extract tables
            for table in doc.tables:
                content += "\n--- Table Content ---\n"
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        content += " | ".join(row_text) + "\n"
            
            return content
            
        except Exception as e:
            raise Exception(f"Error reading Word document: {str(e)}")
    
    async def _extract_powerpoint_content(self, file_path: str) -> str:
        """Extract text from PowerPoint presentations."""
        content = ""
        try:
            presentation = pptx.Presentation(file_path)
            
            for slide_num, slide in enumerate(presentation.slides, 1):
                content += f"\n--- Slide {slide_num} ---\n"
                
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        content += shape.text + "\n"
                    
                    # Extract text from tables in slides
                    if shape.has_table:
                        table = shape.table
                        for row in table.rows:
                            row_text = []
                            for cell in row.cells:
                                if cell.text.strip():
                                    row_text.append(cell.text.strip())
                            if row_text:
                                content += " | ".join(row_text) + "\n"
            
            return content
            
        except Exception as e:
            raise Exception(f"Error reading PowerPoint file: {str(e)}")
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize extracted content."""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Remove page markers and other artifacts
        content = re.sub(r'--- Page \d+ ---', '', content)
        content = re.sub(r'--- Slide \d+ ---', '\n\n', content)
        content = re.sub(r'--- Table Content ---', '\n', content)
        
        # Limit content length for API processing
        if len(content) > self.max_content_length:
            content = content[:self.max_content_length] + "..."
        
        return content.strip()
    
    async def _generate_summary(self, content: str, filename: str) -> str:
        """Generate a comprehensive summary of the document."""
        prompt = f"""
Please provide a comprehensive summary of the following document content.

Document: {filename}
Content: {content}

Requirements:
- Write a clear, well-structured summary in 4-6 sentences
- Focus on the main topics, objectives, and conclusions
- Highlight the most important information and insights
- Use professional, easy-to-understand language
- Capture the essence and purpose of the document

Summary:
"""
        
        try:
            summary = await gemini_service._generate_content(prompt)
            return summary.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return self._generate_fallback_summary(content, filename)
    
    async def _extract_key_points(self, content: str, filename: str) -> List[str]:
        """Extract key points and important information from the document."""
        prompt = f"""
Extract the most important key points from the following document content.

Document: {filename}
Content: {content}

Requirements:
- Identify 5-8 key points that capture the most important information
- Focus on main ideas, conclusions, recommendations, and critical insights
- Each point should be concise but informative (1-2 sentences)
- Present points as a numbered list
- Prioritize actionable insights and significant findings

Format your response as:
1. [First key point]
2. [Second key point]
3. [Third key point]
...

Key Points:
"""
        
        try:
            response = await gemini_service._generate_content(prompt)
            key_points = self._parse_key_points(response)
            return key_points
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return self._generate_fallback_key_points(content)
    
    def _parse_key_points(self, response: str) -> List[str]:
        """Parse the AI response to extract individual key points."""
        key_points = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered points
            if re.match(r'^\d+\.', line):
                # Remove the number and clean up
                point = re.sub(r'^\d+\.\s*', '', line).strip()
                if point:
                    key_points.append(point)
            # Also look for bullet points
            elif line.startswith('•') or line.startswith('-'):
                point = line[1:].strip()
                if point:
                    key_points.append(point)
        
        # If no structured points found, try to split by sentences
        if not key_points:
            sentences = response.split('.')
            for sentence in sentences[:6]:  # Limit to 6 points
                sentence = sentence.strip()
                if len(sentence) > 20:  # Only include substantial sentences
                    key_points.append(sentence + '.')
        
        return key_points[:8]  # Limit to maximum 8 points
    
    def _analyze_document_structure(self, content: str, filename: str) -> Dict:
        """Analyze document structure and determine document type."""
        word_count = len(content.split())
        
        # Determine document type based on content patterns
        doc_type = "General Document"
        if any(keyword in content.lower() for keyword in ['proposal', 'project', 'plan']):
            doc_type = "Project/Proposal Document"
        elif any(keyword in content.lower() for keyword in ['report', 'analysis', 'findings']):
            doc_type = "Report/Analysis"
        elif any(keyword in content.lower() for keyword in ['presentation', 'slide', 'overview']):
            doc_type = "Presentation"
        elif any(keyword in content.lower() for keyword in ['manual', 'guide', 'instructions']):
            doc_type = "Manual/Guide"
        elif any(keyword in content.lower() for keyword in ['research', 'study', 'methodology']):
            doc_type = "Research Document"
        
        # Estimate reading time (average 200 words per minute)
        reading_time = max(1, round(word_count / 200))
        
        return {
            "document_type": doc_type,
            "estimated_reading_time": f"{reading_time} minute{'s' if reading_time != 1 else ''}",
            "complexity": "High" if word_count > 2000 else "Medium" if word_count > 500 else "Low"
        }
    
    def _generate_fallback_summary(self, content: str, filename: str) -> str:
        """Generate a basic summary when AI fails."""
        word_count = len(content.split())
        
        # Extract first few sentences as summary
        sentences = content.split('.')[:3]
        summary_text = '. '.join(sentence.strip() for sentence in sentences if sentence.strip())
        
        if not summary_text:
            summary_text = f"This document contains {word_count} words of content covering various topics and information"
        
        return f"{summary_text}. The document provides comprehensive information that could be valuable for understanding the subject matter."
    
    def _generate_fallback_key_points(self, content: str) -> List[str]:
        """Generate basic key points when AI fails."""
        # Try to find sentences that might be important
        sentences = content.split('.')
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for sentences with important keywords
            if any(keyword in sentence.lower() for keyword in [
                'important', 'key', 'main', 'primary', 'essential', 'critical',
                'conclusion', 'result', 'finding', 'recommendation', 'objective'
            ]):
                if len(sentence) > 20 and len(sentence) < 200:
                    key_points.append(sentence + '.')
                    if len(key_points) >= 5:
                        break
        
        # If no key sentences found, use first few substantial sentences
        if not key_points:
            for sentence in sentences[:5]:
                sentence = sentence.strip()
                if len(sentence) > 30:
                    key_points.append(sentence + '.')
        
        return key_points[:6] if key_points else [
            "Document contains structured information on the main topic.",
            "Content includes detailed explanations and relevant data.",
            "Information is organized to provide comprehensive coverage.",
            "Document serves as a valuable resource for the subject matter."
        ]