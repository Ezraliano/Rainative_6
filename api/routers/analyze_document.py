from fastapi import APIRouter, HTTPException, UploadFile, File
from models.schemas import AnalyzeResponse, VideoMetadata
from services.document_analyzer import DocumentAnalyzer
from services.gemini_utils import generate_content_idea
import logging
import tempfile
import os
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

document_analyzer = DocumentAnalyzer()

@router.post("/analyze-document", response_model=AnalyzeResponse)
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze uploaded document and extract summary with key points.
    Supports PDF, Word, PowerPoint, and text files.
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt', '.ppt', '.pptx'}
    file_extension = Path(file.filename or '').suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed formats: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10MB"
        )
    
    temp_file_path = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Analyze the document
        analysis_result = await document_analyzer.analyze_document(
            temp_file_path, 
            file_extension, 
            file.filename or "document"
        )
        
        # Create enhanced summary with key points
        enhanced_summary = _create_enhanced_summary(analysis_result)
        
        # Generate content recommendations based on document analysis
        recommendations = await generate_content_idea(
            "document", 
            analysis_result["summary"], 
            "This document contains valuable insights that could be repurposed into engaging content."
        )
        
        # Create dummy metadata for document (required by response model)
        dummy_metadata = VideoMetadata(
            video_id="doc_analysis",
            title=file.filename or "Document Analysis",
            duration=0,
            thumbnail_url="",
            channel_name="Document Upload",
            channel_id="",
            view_count=0,
            like_count=0,
            comment_count=0,
            subscriber_count=0,
            published_at=None,
            description=f"Analysis of {file.filename}"
        )
        
        # Calculate a basic viral score based on content quality
        viral_score = _calculate_document_viral_score(analysis_result)
        viral_label = _get_viral_label(viral_score)
        
        return AnalyzeResponse(
            video_metadata=dummy_metadata,
            summary=enhanced_summary,
            timeline_summary=[],  # Not applicable for documents
            viral_score=viral_score,
            viral_label=viral_label,
            viral_explanation=_generate_viral_explanation(analysis_result),
            recommendations=recommendations,
            doc_summary=analysis_result["summary"]
        )
        
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to analyze document: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {str(e)}")

def _create_enhanced_summary(analysis_result: dict) -> str:
    """Create an enhanced summary that includes key points."""
    summary = analysis_result["summary"]
    key_points = analysis_result["key_points"]
    doc_info = analysis_result["document_info"]
    
    enhanced_summary = f"{summary}\n\n"
    
    # Add document information
    enhanced_summary += f"**Document Type:** {doc_info['document_type']}\n"
    enhanced_summary += f"**Reading Time:** {doc_info['estimated_reading_time']}\n"
    enhanced_summary += f"**Content Complexity:** {doc_info['complexity']}\n\n"
    
    # Add key points
    if key_points:
        enhanced_summary += "**Key Points:**\n"
        for i, point in enumerate(key_points, 1):
            enhanced_summary += f"{i}. {point}\n"
    
    return enhanced_summary

def _calculate_document_viral_score(analysis_result: dict) -> int:
    """Calculate a viral potential score for document content."""
    base_score = 50
    
    # Factors that increase viral potential
    word_count = analysis_result.get("word_count", 0)
    key_points_count = len(analysis_result.get("key_points", []))
    doc_type = analysis_result.get("document_info", {}).get("document_type", "")
    
    # Word count factor (optimal range: 500-2000 words)
    if 500 <= word_count <= 2000:
        base_score += 15
    elif 200 <= word_count < 500:
        base_score += 10
    elif word_count > 2000:
        base_score += 5
    
    # Key points factor
    if key_points_count >= 5:
        base_score += 10
    elif key_points_count >= 3:
        base_score += 5
    
    # Document type factor
    if any(keyword in doc_type.lower() for keyword in ["guide", "manual", "research"]):
        base_score += 10
    elif any(keyword in doc_type.lower() for keyword in ["report", "analysis"]):
        base_score += 8
    elif any(keyword in doc_type.lower() for keyword in ["presentation"]):
        base_score += 12
    
    return min(100, max(0, base_score))

def _get_viral_label(score: int) -> str:
    """Get viral potential label based on score."""
    if score >= 80:
        return "Very High Potential"
    elif score >= 60:
        return "Good Potential"
    elif score >= 40:
        return "Moderate Potential"
    else:
        return "Needs Improvement"

def _generate_viral_explanation(analysis_result: dict) -> str:
    """Generate explanation for document's viral potential."""
    doc_info = analysis_result.get("document_info", {})
    word_count = analysis_result.get("word_count", 0)
    key_points_count = len(analysis_result.get("key_points", []))
    
    explanation = f"This {doc_info.get('document_type', 'document').lower()} shows potential for content creation due to its "
    
    factors = []
    
    if word_count > 1000:
        factors.append("comprehensive coverage of the topic")
    elif word_count > 500:
        factors.append("substantial content depth")
    
    if key_points_count >= 5:
        factors.append("multiple actionable insights")
    elif key_points_count >= 3:
        factors.append("clear key takeaways")
    
    if doc_info.get("complexity") == "High":
        factors.append("detailed analysis that can be simplified for broader audiences")
    elif doc_info.get("complexity") == "Medium":
        factors.append("balanced complexity suitable for various content formats")
    
    if factors:
        explanation += ", ".join(factors) + ". "
    
    explanation += "The structured information can be repurposed into engaging social media content, video scripts, or educational materials that resonate with target audiences."
    
    return explanation