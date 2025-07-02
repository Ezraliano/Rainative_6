import React from 'react';
import SummaryCard from './SummaryCard';

const RecentSummaries: React.FC = () => {
  const summaries = [
    {
      id: 1,
      title: 'Machine Learning Basics',
      type: 'YouTube' as const,
      timeAgo: '5 min ago',
      viralScore: 87,
    },
    {
      id: 2,
      title: 'Project Proposal Analysis',
      type: 'PDF' as const,
      timeAgo: '2 hours ago',
      viralScore: 45,
    },
    {
      id: 3,
      title: 'Content Strategy Guide',
      type: 'Word' as const,
      timeAgo: '1 day ago',
      viralScore: 72,
    },
  ];

  return (
    <div className="py-16 bg-gray-800">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-white">Recent Analysis</h2>
          <a href="#" className="text-cyan-400 hover:text-cyan-300 text-sm font-medium transition-colors duration-300">
            View All →
          </a>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {summaries.map((summary) => (
            <SummaryCard
              key={summary.id}
              title={summary.title}
              type={summary.type}
              timeAgo={summary.timeAgo}
              viralScore={summary.viralScore}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecentSummaries;