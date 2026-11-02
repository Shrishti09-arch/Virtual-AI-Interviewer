import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import {
  Settings,
  Cpu,
  CheckCircle,
  AlertCircle,
  Save,
  Key,
  Server,
  User,
  Zap,
  Terminal,
  Copy,
  Check,
  RefreshCw,
  ShieldCheck,
  Download,
  HelpCircle,
} from 'lucide-react';

interface ProviderHealthInfo {
  provider_name: string;
  status: 'connected' | 'offline' | 'unconfigured' | 'no_models' | 'error';
  message: string;
  endpoint: string;
  current_model?: string;
  available_models: string[];
  last_checked?: string;
  install_instructions?: string;
}

interface AIStatusResponse {
  active_provider: string;
  configured_preference: string;
  active_effective_provider: string;
  provider_priority: string[];
  providers: Record<string, ProviderHealthInfo>;
  no_openai_guarantee: boolean;
  ollama_primary: boolean;
}

export const SettingsPage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const toast = useToast();

  // AI Provider State
  const [activeProvider, setActiveProvider] = useState<string>('ollama');
  const [effectiveActive, setEffectiveActive] = useState<string>('fallback_engine');
  const [providerStatuses, setProviderStatuses] = useState<Record<string, ProviderHealthInfo>>({});
  
  // Ollama specific settings
  const [ollamaEndpoint, setOllamaEndpoint] = useState<string>('http://localhost:11434');
  const [selectedOllamaModel, setSelectedOllamaModel] = useState<string>('llama3.1:8b');
  
  // Groq settings
  const [groqKey, setGroqKey] = useState<string>('');
  
  // Test states
  const [testResult, setTestResult] = useState<{ provider: string; success: boolean; message: string; latency_ms?: number } | null>(null);
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  // Candidate Profile Form
  const [fullName, setFullName] = useState<string>(user?.full_name || '');
  const [roleTarget, setRoleTarget] = useState<string>(user?.role_target || 'Full Stack Software Engineer');
  const [experienceLevel, setExperienceLevel] = useState<string>(user?.experience_level || '1-3 years');
  const [skillsString, setSkillsString] = useState<string>((user?.skills || []).join(', '));

  useEffect(() => {
    fetchProviderStatuses();
  }, []);

  const fetchProviderStatuses = async () => {
    setIsRefreshing(true);
    try {
      const res = await apiClient.get('/ai-settings/status');
      const data: AIStatusResponse = res.data;
      setProviderStatuses(data.providers || {});
      setActiveProvider(data.configured_preference || 'ollama');
      setEffectiveActive(data.active_effective_provider || 'fallback_engine');
      
      const ollamaData = data.providers?.ollama;
      if (ollamaData?.current_model) {
        setSelectedOllamaModel(ollamaData.current_model);
      }
    } catch (err) {
      console.error('Failed to fetch provider status:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSelectOllamaModel = async (modelName: string) => {
    setSelectedOllamaModel(modelName);
    try {
      await apiClient.post('/ai-settings/select-model', {
        provider: 'ollama',
        model_name: modelName,
      });
      await fetchProviderStatuses();
    } catch (err) {
      console.error('Failed to switch Ollama model:', err);
    }
  };

  const handleTestConnection = async (provider: string) => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await apiClient.post('/ai-settings/test', {
        provider,
        api_key: provider === 'groq' ? groqKey : undefined,
        endpoint: provider === 'ollama' ? ollamaEndpoint : undefined,
        model_name: provider === 'ollama' ? selectedOllamaModel : undefined,
      });
      setTestResult({
        provider,
        success: res.data.success,
        message: res.data.message || (res.data.success ? 'Verified live connection successfully' : 'Failed connection test'),
        latency_ms: res.data.latency_ms,
      });
      await fetchProviderStatuses();
    } catch (err: any) {
      setTestResult({
        provider,
        success: false,
        message: err.response?.data?.detail || `Connection to ${provider} failed`,
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSaveAISettings = async () => {
    setIsSaving(true);
    try {
      await apiClient.put('/auth/ai-preferences', {
        llm_preference: activeProvider,
        groq_api_key: groqKey || undefined,
        ollama_endpoint: ollamaEndpoint || undefined,
      });
      await refreshUser();
      await fetchProviderStatuses();
      toast.success('AI Configuration updated successfully!');
    } catch (err) {
      console.error('Failed to save AI preferences:', err);
      toast.error('Failed to save AI preferences.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      await apiClient.put('/auth/profile', {
        full_name: fullName,
        role_target: roleTarget,
        experience_level: experienceLevel,
        skills: skillsString.split(',').map((s) => s.trim()).filter(Boolean),
      });
      await refreshUser();
      toast.success('Profile updated successfully!');
    } catch (err) {
      console.error('Failed to update profile:', err);
      toast.error('Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  const copyToClipboard = (cmd: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedCmd(cmd);
    toast.info('Copied command to clipboard!');
    setTimeout(() => setCopiedCmd(null), 2500);
  };

  const ollamaHealth = providerStatuses.ollama;
  const isOllamaConnected = ollamaHealth?.status === 'connected';

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">
      {/* Title & OpenAI Prohibition Policy Banner */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-slate-100 flex items-center gap-2">
              <Cpu className="w-6 h-6 text-indigo-400" />
              <span>Modular AI Provider Engine</span>
            </h1>
            <p className="text-xs text-slate-400">
              Zero OpenAI APIs. Prioritizes local open models via Ollama and LM Studio with verified connection checks.
            </p>
          </div>

          <button
            onClick={fetchProviderStatuses}
            disabled={isRefreshing}
            className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs text-slate-300 border border-slate-700 flex items-center gap-1.5 transition-colors self-start"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
            <span>Check All Providers</span>
          </button>
        </div>

        {/* Strictly No OpenAI API Banner */}
        <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-indigo-950/40 border border-emerald-500/30 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
            <div>
              <div className="text-xs font-bold text-emerald-300">Strictly Open-Source & Local AI Policy</div>
              <div className="text-[11px] text-slate-400">
                100% free of proprietary OpenAI APIs. Uses locally hosted weights (Ollama/LM Studio), open Hugging Face providers, or free Groq LPU models.
              </div>
            </div>
          </div>
          <span className="text-[10px] px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30 shrink-0">
            No OpenAI Required
          </span>
        </div>
      </div>

      {/* AI Priority Chain Summary Pill Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
          <span>Configured Priority Hierarchy</span>
          <span className="text-indigo-400">
            Currently Effective Engine:{' '}
            <strong className="text-slate-100 uppercase underline decoration-indigo-500">{effectiveActive}</strong>
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1 px-3 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-semibold">
            <span>1. Ollama (Primary)</span>
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1 px-3 py-1 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/40 font-semibold">
            <span>2. LM Studio (Secondary Local)</span>
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1 px-3 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold">
            <span>3. Hugging Face Inference</span>
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1 px-3 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 font-semibold">
            <span>4. Groq Free Models</span>
          </div>
          <span className="text-slate-600">→</span>
          <div className="flex items-center gap-1 px-3 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
            <span>5. Fallback Rule Engine</span>
          </div>
        </div>
      </div>

      {/* SECTION 1: OLLAMA PRIMARY PROVIDER CARD */}
      <div className="p-6 rounded-3xl bg-slate-900 border-2 border-indigo-500/40 shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 font-black text-lg">
              🦙
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-100 text-base">Ollama Local Server</h3>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30">
                  Primary Provider
                </span>
              </div>
              <p className="text-xs text-slate-400">Endpoint: http://localhost:11434/api/generate</p>
            </div>
          </div>

          {/* Connection Status Badge */}
          <div className="flex items-center gap-2">
            <span
              className={`text-xs px-3 py-1.5 rounded-xl font-bold flex items-center gap-1.5 border ${
                isOllamaConnected
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : ollamaHealth?.status === 'no_models'
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isOllamaConnected
                    ? 'bg-emerald-400'
                    : ollamaHealth?.status === 'no_models'
                    ? 'bg-amber-400 animate-pulse'
                    : 'bg-rose-400'
                }`}
              />
              <span>
                {isOllamaConnected
                  ? 'Verified Online'
                  : ollamaHealth?.status === 'no_models'
                  ? 'Running (No Models)'
                  : 'Offline / Unreachable'}
              </span>
            </span>

            <button
              onClick={() => handleTestConnection('ollama')}
              disabled={isTesting}
              className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all disabled:opacity-50"
            >
              {isTesting ? 'Verifying...' : 'Test Connection'}
            </button>
          </div>
        </div>

        {/* Message / Last Status */}
        {ollamaHealth && (
          <div className="p-3.5 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
            {isOllamaConnected ? (
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <span className="font-semibold">{ollamaHealth.message}</span>
              {ollamaHealth.last_checked && (
                <span className="text-slate-500 ml-2">(Checked: {ollamaHealth.last_checked})</span>
              )}
            </div>
          </div>
        )}

        {/* Model Selection Dropdown */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Current Model (Auto-detected: qwen3:8b, llama3.1:8b, mistral:7b)
            </label>
            {ollamaHealth?.available_models && ollamaHealth.available_models.length > 0 ? (
              <select
                value={selectedOllamaModel}
                onChange={(e) => handleSelectOllamaModel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {ollamaHealth.available_models.map((m) => (
                  <option key={m} value={m}>
                    {m} {m === selectedOllamaModel ? '(Selected)' : ''}
                  </option>
                ))}
              </select>
            ) : (
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-500">
                No installed models detected yet. Pull a model below.
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Ollama Server Endpoint</label>
            <input
              type="text"
              value={ollamaEndpoint}
              onChange={(e) => setOllamaEndpoint(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
        </div>

        {/* Windows Installation Instructions (If Ollama is offline or has no models) */}
        {(!isOllamaConnected || ollamaHealth?.status === 'no_models') && (
          <div className="p-5 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 space-y-3">
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
              <Terminal className="w-4 h-4" />
              <span>
                {ollamaHealth?.status === 'no_models'
                  ? 'Step 2: Pull a Recommended Model into Ollama'
                  : 'Windows Installation & Setup Instructions'}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {ollamaHealth?.status === 'no_models'
                ? 'Ollama is installed and running, but has no model weights loaded. Open PowerShell and run one of these commands to download a recommended model:'
                : 'Ollama allows running powerful models locally on your PC with zero API fees and complete data privacy.'}
            </p>

            <div className="space-y-2">
              {[
                { label: 'Option A (Meta Llama 3.1 8B - Recommended)', cmd: 'ollama run llama3.1:8b' },
                { label: 'Option B (Alibaba Qwen 2.5 8B - High Coding Precision)', cmd: 'ollama run qwen2.5:8b' },
                { label: 'Option C (Mistral 7B Instruct - Ultra Fast)', cmd: 'ollama run mistral:7b' },
                { label: 'Install Ollama via winget (PowerShell)', cmd: 'winget install Ollama.Ollama' },
              ].map(({ label, cmd }) => (
                <div
                  key={cmd}
                  className="flex items-center justify-between bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono"
                >
                  <div className="truncate mr-2">
                    <span className="text-[10px] text-slate-500 block font-sans">{label}</span>
                    <span className="text-indigo-300">{cmd}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(cmd)}
                    className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-900 border border-slate-800 shrink-0 transition-colors"
                    title="Copy command"
                  >
                    {copiedCmd === cmd ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* SECTION 2: OTHER MODULAR PROVIDERS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* LM Studio Card */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 font-bold text-sm">
                LM
              </div>
              <div>
                <h4 className="font-bold text-slate-100 text-sm">LM Studio (Secondary Local)</h4>
                <p className="text-[11px] text-slate-400">http://localhost:1234/v1</p>
              </div>
            </div>
            <span
              className={`text-[10px] px-2.5 py-1 rounded-full font-bold border ${
                providerStatuses.lmstudio?.status === 'connected'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-slate-800 text-slate-500 border-slate-700'
              }`}
            >
              {providerStatuses.lmstudio?.status === 'connected' ? 'Connected' : 'Offline'}
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Local OpenAI-compatible server. Start the server in LM Studio on port 1234 to enable secondary local inference.
          </p>
          <button
            onClick={() => handleTestConnection('lmstudio')}
            disabled={isTesting}
            className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
          >
            Test LM Studio
          </button>
        </div>

        {/* Groq Free Models Card */}
        <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-bold text-sm">
                ⚡
              </div>
              <div>
                <h4 className="font-bold text-slate-100 text-sm">Groq Free Cloud Models</h4>
                <p className="text-[11px] text-slate-400">Llama-3.3-70b-versatile</p>
              </div>
            </div>
            <span
              className={`text-[10px] px-2.5 py-1 rounded-full font-bold border ${
                providerStatuses.groq?.status === 'connected'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-slate-800 text-slate-500 border-slate-700'
              }`}
            >
              {providerStatuses.groq?.status === 'connected' ? 'Connected' : 'Unconfigured'}
            </span>
          </div>
          <div>
            <label className="text-[11px] font-semibold text-slate-400 block mb-1">
              Optional Free Groq API Key (from console.groq.com)
            </label>
            <input
              type="password"
              placeholder="gsk_..."
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 font-mono"
            />
          </div>
          <button
            onClick={() => handleTestConnection('groq')}
            disabled={isTesting}
            className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700"
          >
            Test Groq
          </button>
        </div>
      </div>

      {/* SECTION 3: FALLBACK ENGINE CARD */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold text-sm">
              ⚙️
            </div>
            <div>
              <h4 className="font-bold text-slate-100 text-sm">Deterministic Rule-Based Fallback Engine</h4>
              <p className="text-[11px] text-slate-400">In-Memory Rule & Heuristic Evaluator</p>
            </div>
          </div>
          <span className="text-[10px] px-2.5 py-1 rounded-full font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            Active Fallback
          </span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          When external or local AI models are unreachable, the system automatically runs structured heuristic grading,
          ATS keyword matching, and template-based roadmaps. All fallback outputs are clearly flagged with an{' '}
          <strong className="text-amber-400">"AI Provider Offline"</strong> badge to ensure transparency.
        </p>
      </div>

      {/* Test Result Callout */}
      {testResult && (
        <div
          className={`p-4 rounded-2xl border text-xs leading-relaxed flex items-start gap-2.5 ${
            testResult.success
              ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
              : 'bg-rose-950/30 border-rose-500/40 text-rose-300'
          }`}
        >
          {testResult.success ? (
            <CheckCircle className="w-4 h-4 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          )}
          <div>
            <span className="font-bold uppercase tracking-wider">{testResult.provider}: </span>
            <span>{testResult.message}</span>
            {testResult.latency_ms !== undefined && (
              <span className="ml-2 font-mono">({testResult.latency_ms}ms)</span>
            )}
          </div>
        </div>
      )}

      {/* Save AI Preferences Action Bar */}
      <div className="flex justify-end">
        <button
          onClick={handleSaveAISettings}
          disabled={isSaving}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition-all disabled:opacity-50"
        >
          <Save className="w-3.5 h-3.5" />
          <span>{isSaving ? 'Saving Preferences...' : 'Save AI Configuration'}</span>
        </button>
      </div>

      {/* Candidate Profile Form */}
      <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-5">
        <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
          <User className="w-4 h-4 text-indigo-400" />
          <span>Candidate Career Profile</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 mt-1 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400">Target Role Title</label>
            <input
              type="text"
              value={roleTarget}
              onChange={(e) => setRoleTarget(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 mt-1 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400">Experience Level</label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 mt-1 focus:outline-none focus:border-indigo-500"
            >
              <option value="Student/Fresher">Student / Fresher</option>
              <option value="1-3 years">1-3 years (Junior / Mid)</option>
              <option value="4-7 years">4-7 years (Senior)</option>
              <option value="8+ years">8+ years (Staff / Principal)</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400">Core Technical Skills (comma separated)</label>
            <input
              type="text"
              value={skillsString}
              onChange={(e) => setSkillsString(e.target.value)}
              placeholder="e.g. React, TypeScript, FastAPI, PostgreSQL, Docker"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 mt-1 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <button
          onClick={handleSaveProfile}
          disabled={isSaving}
          className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center gap-2 shadow-md transition-all hover:scale-[1.01]"
        >
          <Save className="w-4 h-4" />
          <span>Save Profile</span>
        </button>
      </div>
    </div>
  );
};
