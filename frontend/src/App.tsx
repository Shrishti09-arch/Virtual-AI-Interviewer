import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { MockInterviewPage } from './pages/MockInterviewPage';
import { ResumeAnalyzerPage } from './pages/ResumeAnalyzerPage';
import { ResumeBuilderPage } from './pages/ResumeBuilderPage';
import { JobMatcherPage } from './pages/JobMatcherPage';
import { PracticePage } from './pages/PracticePage';
import { RoadmapPage } from './pages/RoadmapPage';
import { SettingsPage } from './pages/SettingsPage';
import { InterviewHistoryPage } from './pages/InterviewHistoryPage';
import { AuthPage } from './pages/AuthPage';

export function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans transition-colors duration-200">
              <Navbar />
              <div className="flex-1 flex overflow-hidden">
                <Sidebar />
                <main className="flex-1 overflow-y-auto bg-slate-950/90 pb-12 transition-colors">
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/login" element={<AuthPage />} />
                    <Route
                      path="/dashboard"
                      element={
                        <ProtectedRoute>
                          <DashboardPage initialTab="overview" />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/progress"
                      element={
                        <ProtectedRoute>
                          <DashboardPage initialTab="progress" />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/history"
                      element={
                        <ProtectedRoute>
                          <InterviewHistoryPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/mock-interview"
                      element={
                        <ProtectedRoute>
                          <MockInterviewPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/resume-analyzer"
                      element={
                        <ProtectedRoute>
                          <ResumeAnalyzerPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/resume-builder"
                      element={
                        <ProtectedRoute>
                          <ResumeBuilderPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/jd-matcher"
                      element={
                        <ProtectedRoute>
                          <JobMatcherPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/practice"
                      element={
                        <ProtectedRoute>
                          <PracticePage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/roadmap"
                      element={
                        <ProtectedRoute>
                          <RoadmapPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/settings"
                      element={
                        <ProtectedRoute>
                          <SettingsPage />
                        </ProtectedRoute>
                      }
                    />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </main>
              </div>
            </div>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
