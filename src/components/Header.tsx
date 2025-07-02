import React from 'react';
import { Sparkles, LogOut } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="flex justify-between items-center py-6 px-6 bg-gray-900 border-b border-gray-800">
      <div className="flex items-center">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent flex items-center">
          <Sparkles className="h-8 w-8 mr-3 text-cyan-400" />
          Rainative AI
        </h1>
      </div>
      <button className="px-6 py-3 border border-gray-600 rounded-xl text-gray-300 hover:bg-gray-800 hover:text-white transition-all duration-300 text-sm flex items-center">
        <LogOut className="h-4 w-4 mr-2" />
        Sign out
      </button>
    </header>
  );
};

export default Header;