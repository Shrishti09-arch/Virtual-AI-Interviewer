export const formatDate = (dateStr: string): string => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

export const getScoreBadgeClass = (score: number): string => {
  if (score >= 85) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  if (score >= 70) return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
  if (score >= 50) return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
};

export const getVerdictBadgeClass = (verdict: string): string => {
  switch (verdict) {
    case 'Strong Hire':
      return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    case 'Hire':
      return 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30';
    case 'Lean Hire':
      return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
    default:
      return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
  }
};

export const formatDurationSeconds = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};
