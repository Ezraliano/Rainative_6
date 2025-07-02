import React from 'react';
import { FileText, Youtube, FileType, TrendingUp } from 'lucide-react';

type SummaryType = 'YouTube' | 'PDF' | 'Word';

interface SummaryCardProps {
  title: string;
  type: SummaryType;
  timeAgo: string;
  viralScore?: number;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ title, type, timeAgo, viralScore }) => {
  const getIcon = () => {
    switch (type) {
      case 'YouTube':
        return <Youtube className="h-5 w-5 text-red-400" />;
      case 'PDF':
        return <FileText className="h-5 w-5 text-blue-400" />;
      case 'Word':
        return <FileType className="h-5 w-5 text-indigo-400" />;
      default:
        return <FileText className="h-5 w-5 text-gray-400" />;
    }
  };

  const getTypeClass = () => {
    switch (type) {
      case 'YouTube':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'PDF':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'Word':
        return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const getViralScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gray-900 p-6 rounded-xl border border-gray-700 hover:border-gray-600 transition-all duration-300 cursor-pointer group hover:shadow-xl">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          {getIcon()}
          <span className={`ml-3 text-xs font-medium py-1 px-3 rounded-full border ${getTypeClass()}`}>
            {type}
          </span>
        </div>
        <span className="text-xs text-gray-500">{timeAgo}</span>
      </div>
      
      <h3 className="font-semibold text-white mb-3 group-hover:text-cyan-400 transition-colors duration-300">
        {title}
      </h3>
      
      {viralScore !== undefined && (
        <div className="flex items-center justify-between pt-3 border-t border-gray-700">
          <div className="flex items-center">
            <TrendingUp className="h-4 w-4 text-gray-400 mr-2" />
            <span className="text-xs text-gray-400">Viral Score</span>
          </div>
          <span className={`text-sm font-bold ${getViralScoreColor(viralScore)}`}>
            {viralScore}/100
          </span>
        </div>
      )}
    </div>
  );
};

export default SummaryCard;