import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import WebAutomation from './pages/WebAutomation';
import DataProfiling from './pages/DataProfiling';
import LLMQuery from './pages/LLMQuery';
import Home from './pages/Home';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
        
        <main className={`flex-1 overflow-hidden transition-all duration-300 ${
          sidebarOpen ? 'ml-64' : 'ml-20'
        }`}>
          <div className="h-full overflow-y-auto">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/llm-query" element={<LLMQuery />} />
              <Route path="/web-automation" element={<WebAutomation />} />
              <Route path="/data-profiling" element={<DataProfiling />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
