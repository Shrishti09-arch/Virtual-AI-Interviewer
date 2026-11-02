import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSearch,
  FileText,
  FileCheck,
  Code2,
  Video,
  Milestone,
  TrendingUp,
  History,
  Settings,
  Sparkles,
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Resume Analyzer', path: '/resume-analyzer', icon: FileSearch, badge: 'ATS' },
  { name: 'AI Resume Builder', path: '/resume-builder', icon: FileText, badge: 'Builder' },
  { name: 'Job Description Matcher', path: '/jd-matcher', icon: FileCheck, badge: 'Match' },
  { name: 'Technical Interview Practice', path: '/practice', icon: Code2 },
  { name: 'Virtual Mock Interview', path: '/mock-interview', icon: Video, badge: 'Live AI' },
  { name: 'Career Roadmap', path: '/roadmap', icon: Milestone },
  { name: 'My Progress', path: '/progress', icon: TrendingUp, badge: 'Metrics' },
  { name: 'Interview History', path: '/history', icon: History, badge: 'Scorecard' },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/60 dark:bg-slate-900/60 flex flex-col justify-between p-4 shrink-0 transition-colors">
      <div className="space-y-6">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3">
          Navigation
        </div>

        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600/20 to-purple-600/10 text-indigo-400 border border-indigo-500/30 font-bold shadow-inner'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span className="truncate">{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/25 shrink-0">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Career Coach Pro Tip card */}
      <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-950/60 to-slate-900 border border-indigo-500/20 shadow-md">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs mb-1.5">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Interviewer Insight</span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Use the <strong className="text-slate-200">STAR method</strong>: Situation, Task, Action, and Quantified Result to maximize hire ratings.
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
