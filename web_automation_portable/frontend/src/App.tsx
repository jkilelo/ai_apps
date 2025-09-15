import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/layout/Navigation';
import { DataProfilingFlow } from './flows/data-profiling/DataProfilingFlow';
// import { WebAutomationFlow } from './flows/web-automation/WebAutomationFlow';
import { WebAutomationFlowSimplified } from './flows/web-automation/WebAutomationFlowSimplified';
import { HomePage } from './pages/HomePage';
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
    return (
        <ThemeProvider>
            <Router>
                <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
                    <Navigation />
                    <main>
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/data-profiling" element={<DataProfilingFlow />} />
                            <Route path="/web-automation" element={<WebAutomationFlowSimplified />} />
                        </Routes>
                    </main>
                </div>
            </Router>
        </ThemeProvider>
    );
}

export default App;
