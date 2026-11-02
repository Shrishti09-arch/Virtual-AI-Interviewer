import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { Bot, LogOut, Cpu, ShieldCheck, Sun, Moon } from 'lucide-react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { ConfirmationModal } from './ConfirmationModal';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const toast = useToast();
  const [showLogoutModal, setShowLogoutModal] = useState<boolean>(false);
  const [providerInfo, setProviderInfo] = useState<{
    effective_provider: string;
    is_connected: boolean;
    model_name: string;
  }>({
    effective_provider: 'fallback_engine',
    is_connected: false,
    model_name: 'rule-based-heuristics',
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await apiClient.get('/ai-settings/status');
        const active = res.data.active_effective_provider;
        const providerData = res.data.providers?.[active];
        setProviderInfo({
          effective_provider: active,
          is_connected: providerData?.status === 'connected',
          model_name: providerData?.current_model || active,
        });
      } catch {
        // Fallback default
      }
    };
    fetchStatus();
  }, []);

  const handleConfirmLogout = () => {
    setShowLogoutModal(false);
    logout();
    toast.info('You have been signed out successfully.', 'Signed Out');
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40 px-6 flex items-center justify-between transition-colors">
      <div className="flex items-center gap-3">
        <Link to="/dashboard" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Bot className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <div className="font-bold text-slate-100 tracking-tight flex items-center gap-1.5 text-base">
              <span>Virtual AI Interviewer</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                AI Coach
              </span>
            </div>
            <div className="text-xs text-slate-400 hidden sm:block">
              {user?.role_target || 'Target: Software Engineer'}
            </div>
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-3">
        {/* Strictly No OpenAI Badge */}
        <div className="hidden lg:flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-[10px] font-semibold text-emerald-300">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Local & Open AI (No OpenAI)</span>
        </div>

        {/* Verified AI Engine Pill */}
        <Link
          to="/settings"
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300 hover:border-indigo-500/50 hover:bg-slate-800 transition-colors"
          title={`Verified Engine: ${providerInfo.effective_provider}`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              providerInfo.effective_provider === 'ollama' && providerInfo.is_connected
                ? 'bg-emerald-400 animate-pulse'
                : providerInfo.is_connected
                ? 'bg-cyan-400'
                : 'bg-amber-400'
            }`}
          />
          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          <span>Engine:</span>
          <span className="font-semibold text-indigo-300 uppercase">
            {providerInfo.effective_provider === 'ollama'
              ? `Ollama (${providerInfo.model_name})`
              : providerInfo.effective_provider === 'fallback_engine'
              ? 'Heuristic Fallback Engine'
              : providerInfo.effective_provider}
          </span>
        </Link>

        {/* Theme Toggle (Dark / Light Mode) */}
        <button
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors border border-slate-800"
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-indigo-400" />
          )}
        </button>

        {/* User Profile Info & Logout */}
        {user && (
          <div className="flex items-center gap-3 pl-2 border-l border-slate-800">
            <div className="text-right hidden sm:block">
              <div className="text-xs font-bold text-slate-200">{user.full_name || user.name}</div>
              <div className="text-[10px] text-slate-400">{user.experience_level || '1-3 years'}</div>
            </div>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shadow-md">
              {(user.full_name || user.name || 'C').charAt(0).toUpperCase()}
            </div>
            <button
              onClick={() => setShowLogoutModal(true)}
              title="Sign Out"
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 rounded-xl transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Logout Confirmation Dialog */}
      <ConfirmationModal
        isOpen={showLogoutModal}
        title="Sign Out of Your Account"
        message="Are you sure you want to end your current session? You will need to sign in again to access your roadmaps, practice drills, and scorecard analytics."
        confirmText="Sign Out"
        cancelText="Stay Signed In"
        isDestructive={true}
        icon="danger"
        onConfirm={handleConfirmLogout}
        onCancel={() => setShowLogoutModal(false)}
      />
    </header>
  );
};

export default Navbar;
