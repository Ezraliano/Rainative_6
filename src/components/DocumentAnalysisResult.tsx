import React from 'react';
import { FileText, Clock, Target, Lightbulb, ArrowLeft, CheckCircle } from 'lucide-react';

interface DocumentInfo {
  document_type: string;
  estimated_reading_time: string;
  complexity: string;
}

interface AnalysisData {
  summary: string;
  key_points?: string[];
  document_info?: DocumentInfo;
  word_count?: number;
  content_preview?: string;
  viral_score: number;
  viral_label: string;
  viral_explanation: string;
  recommendations: {
    title: string;
    target_audience: string;
    content_style: string;
    suggested_structure: {
      hook: string;
      introduction: string;
      main_content: string;
      call_to_action: string;
    };
    pro_tips: string[];
    estimated_viral_score: number;
  };
}

interface DocumentAnalysisResultProps {
  analysisData: AnalysisData;
  filename: string;
  onBack: () => void;
}

const DocumentAnalysisResult: React.FC<DocumentAnalysisResultProps> = ({
  analysisData,
  filename,
  onBack
}) => {
  const parseKeyPoints = (summary: string): string[] => {
    // Extract key points from the enhanced summary
    const keyPointsSection = summary.split('**Key Points:**')[1];
    if (!keyPointsSection) return [];
    
    const points = keyPointsSection
      .split('\n')
      .filter(line => line.trim().match(/^\d+\./))
      .map(line => line.replace(/^\d+\.\s*/, '').trim())
      .filter(point => point.length > 0);
    
    return points;
  };

  const getCleanSummary = (summary: string): string => {
    // Extract just the main summary text before document info
    return summary.split('\n\n**Document Type:**')[0].trim();
  };

  const extractDocumentInfo = (summary: string): DocumentInfo | null => {
    const docTypeMatch = summary.match(/\*\*Document Type:\*\* (.+)/);
    const readingTimeMatch = summary.match(/\*\*Reading Time:\*\* (.+)/);
    const complexityMatch = summary.match(/\*\*Content Complexity:\*\* (.+)/);
    
    if (docTypeMatch && readingTimeMatch && complexityMatch) {
      return {
        document_type: docTypeMatch[1],
        estimated_reading_time: readingTimeMatch[1],
        complexity: complexityMatch[1]
      };
    }
    return null;
  };

  const keyPoints = parseKeyPoints(analysisData.summary);
  const cleanSummary = getCleanSummary(analysisData.summary);
  const documentInfo = extractDocumentInfo(analysisData.summary) || analysisData.document_info;

  const getComplexityColor = (complexity: string) => {
    switch (complexity?.toLowerCase()) {
      case 'high': return 'text-red-400 bg-red-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'low': return 'text-green-400 bg-green-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto mt-8 px-4">
      <div className="bg-gray-900 rounded-2xl p-6 md:p-8 shadow-2xl">
        {/* Header */}
        <div className="flex flex-col lg:flex-row gap-8 mb-8">
          {/* Document Preview */}
          <div className="w-full lg:w-1/3">
            <div className="bg-gray-800 rounded-xl p-8 border border-gray-700 text-center">
              <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl mx-auto mb-4">
                <FileText className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-white text-xl font-semibold mb-2">{filename}</h3>
              
              {documentInfo && (
                <div className="space-y-3 mt-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Type:</span>
                    <span className="text-cyan-400 font-medium">{documentInfo.document_type}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Reading Time:</span>
                    <span className="text-white flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {documentInfo.estimated_reading_time}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Complexity:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getComplexityColor(documentInfo.complexity)}`}>
                      {documentInfo.complexity}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Summary Section */}
          <div className="w-full lg:w-2/3">
            <h2 className="text-3xl font-bold text-white mb-6 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Document Summary
            </h2>
            <p className="text-gray-300 mb-6 text-lg leading-relaxed">
              {cleanSummary}
            </p>
          </div>
        </div>

        {/* Key Points Section */}
        {keyPoints.length > 0 && (
          <div className="mb-8">
            <h3 className="text-2xl font-semibold text-white mb-6 flex items-center">
              <CheckCircle className="w-6 h-6 mr-3 text-green-400" />
              Key Points & Important Information
            </h3>
            <div className="grid gap-4">
              {keyPoints.map((point, index) => (
                <div key={index} className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-colors duration-200">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mr-4 mt-1">
                      <span className="text-white font-bold text-sm">{index + 1}</span>
                    </div>
                    <p className="text-gray-300 leading-relaxed flex-1">{point}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content Recommendations */}
        <div className="mb-8">
          <h3 className="text-2xl font-semibold text-white mb-6 flex items-center">
            <Lightbulb className="w-6 h-6 mr-3 text-yellow-400" />
            Content Creation Recommendations
          </h3>
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-semibold text-cyan-400 mb-4">📝 Repurpose Strategy</h4>
                <h5 className="text-white font-medium mb-3">{analysisData.recommendations.title}</h5>
                
                <div className="space-y-4">
                  <div className="flex items-start">
                    <Target className="w-5 h-5 text-green-400 mr-3 mt-1 flex-shrink-0" />
                    <div>
                      <h6 className="text-white font-medium mb-1">Target Audience</h6>
                      <p className="text-gray-300 text-sm">{analysisData.recommendations.target_audience}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <FileText className="w-5 h-5 text-blue-400 mr-3 mt-1 flex-shrink-0" />
                    <div>
                      <h6 className="text-white font-medium mb-1">Content Style</h6>
                      <p className="text-gray-300 text-sm">{analysisData.recommendations.content_style}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-purple-400 mb-4">💡 Pro Tips</h4>
                <ul className="space-y-2">
                  {analysisData.recommendations.pro_tips.map((tip, index) => (
                    <li key={index} className="flex items-start text-gray-300 text-sm">
                      <span className="text-cyan-400 mr-2 mt-1">•</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Viral Potential */}
        <div className="mb-8 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl p-6 border border-purple-500/30">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <span className="text-2xl mr-3">🚀</span>
            Content Viral Potential
          </h3>
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-300">Estimated Score:</span>
            <div className="flex items-center">
              <div className="w-32 h-2 bg-gray-700 rounded-full mr-3">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full transition-all duration-1000"
                  style={{ width: `${analysisData.viral_score}%` }}
                ></div>
              </div>
              <span className="text-white font-bold">{analysisData.viral_score}/100</span>
            </div>
          </div>
          <p className="text-gray-300 text-sm leading-relaxed">
            {analysisData.viral_explanation}
          </p>
        </div>

        {/* Back Button */}
        <button
          onClick={onBack}
          className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-300 shadow-lg hover:shadow-xl"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Analyze Another Document
        </button>
      </div>
    </div>
  );
};

export default DocumentAnalysisResult;