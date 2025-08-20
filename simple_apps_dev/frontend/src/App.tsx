import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/layout/Navigation';
import { DataProfilingFlowCompact } from './flows/data-profiling/DataProfilingFlowCompact';
import { WebAutomationFlowVertical } from './flows/web-automation/WebAutomationFlowVertical';
import { HomePage } from './pages/HomePage';
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
    return (
        <ThemeProvider>
            <Router>
                <div className="min-h-screen">
                    <Navigation />
                    <main>
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/data-profiling" element={<DataProfilingFlowCompact />} />
                            <Route path="/web-automation" element={<WebAutomationFlowVertical />} />
                        </Routes>
                    </main>
                </div>
            </Router>
        </ThemeProvider>
    );
}

export default App;
