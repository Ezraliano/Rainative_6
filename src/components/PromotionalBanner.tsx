import React from 'react';
import { Zap, TrendingUp, Target, Sparkles } from 'lucide-react';

const PromotionalBanner: React.FC = () => {
  return (
    <div className="w-full px-4 sm:px-6 py-16 bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10"></div>
      <div className="absolute top-0 left-0 w-full h-full">
        <div className="absolute top-10 left-10 w-20 h-20 bg-cyan-500/20 rounded-full blur-xl"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-purple-500/20 rounded-full blur-xl"></div>
        <div className="absolute top-1/2 left-1/2 w-40 h-40 bg-blue-500/10 rounded-full blur-2xl transform -translate-x-1/2 -translate-y-1/2"></div>
      </div>
      
      <div className="max-w-6xl mx-auto text-center relative z-10">
        <h2 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-8">
          <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Ready to Go Viral?
          </span>
        </h2>
        <p className="text-xl sm:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
          Join thousands of content creators who use Rainative AI to analyze, optimize, and create viral content 
          that reaches millions of viewers worldwide.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
          <button className="w-full sm:w-auto bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold px-10 py-5 rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all duration-300 inline-flex items-center justify-center shadow-2xl hover:shadow-cyan-500/25 text-lg">
            <Zap className="h-6 w-6 mr-3" />
            Start Creating Now
          </button>
          <button className="w-full sm:w-auto bg-gray-800 border border-gray-600 text-white font-semibold px-10 py-5 rounded-xl hover:bg-gray-700 hover:border-gray-500 transition-all duration-300 text-lg">
            View Pricing Plans
          </button>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          <div className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 hover:border-cyan-500/50 transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <TrendingUp className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">Viral Analysis</h3>
            <p className="text-gray-300 leading-relaxed">
              Get detailed viral potential scores and understand what makes content shareable and engaging.
            </p>
          </div>
          
          <div className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 hover:border-purple-500/50 transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">AI Summaries</h3>
            <p className="text-gray-300 leading-relaxed">
              Extract key insights from any content with timeline breakdowns and comprehensive analysis.
            </p>
          </div>
          
          <div className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 hover:border-blue-500/50 transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Target className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">Smart Recommendations</h3>
            <p className="text-gray-300 leading-relaxed">
              Receive personalized content ideas and strategies to maximize your reach and engagement.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromotionalBanner;