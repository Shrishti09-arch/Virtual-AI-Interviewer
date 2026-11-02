import React from 'react';

export const Shimmer: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`animate-pulse bg-slate-800/60 rounded-xl ${className}`} />
);

export const MetricSkeleton: React.FC = () => (
  <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
    <div className="flex items-center justify-between">
      <Shimmer className="h-3 w-24" />
      <Shimmer className="h-8 w-8 rounded-lg" />
    </div>
    <Shimmer className="h-8 w-16" />
    <Shimmer className="h-2 w-full rounded-full" />
    <Shimmer className="h-3 w-32" />
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
    <div className="flex items-center justify-between">
      <div className="space-y-1">
        <Shimmer className="h-4 w-40" />
        <Shimmer className="h-3 w-64" />
      </div>
      <Shimmer className="h-4 w-28" />
    </div>
    <div className="h-64 w-full flex items-end gap-3 pt-6 px-2">
      <Shimmer className="h-32 flex-1 rounded-t-lg" />
      <Shimmer className="h-48 flex-1 rounded-t-lg" />
      <Shimmer className="h-24 flex-1 rounded-t-lg" />
      <Shimmer className="h-56 flex-1 rounded-t-lg" />
      <Shimmer className="h-40 flex-1 rounded-t-lg" />
      <Shimmer className="h-44 flex-1 rounded-t-lg" />
      <Shimmer className="h-60 flex-1 rounded-t-lg" />
    </div>
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 4 }) => (
  <div className="space-y-3 p-4 rounded-3xl bg-slate-900/60 border border-slate-800">
    <div className="flex justify-between items-center pb-2 border-b border-slate-800">
      <Shimmer className="h-4 w-36" />
      <Shimmer className="h-7 w-24 rounded-lg" />
    </div>
    <div className="space-y-2.5">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-3 rounded-xl bg-slate-950/40">
          <Shimmer className="h-8 w-8 rounded-lg shrink-0" />
          <div className="flex-1 space-y-1.5">
            <Shimmer className="h-3.5 w-48" />
            <Shimmer className="h-2.5 w-32" />
          </div>
          <Shimmer className="h-6 w-16 rounded-full" />
        </div>
      ))}
    </div>
  </div>
);

export const QuestionCardSkeleton: React.FC = () => (
  <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
    <div className="flex items-center justify-between">
      <Shimmer className="h-4 w-28" />
      <Shimmer className="h-5 w-20 rounded-full" />
    </div>
    <Shimmer className="h-5 w-3/4" />
    <Shimmer className="h-16 w-full rounded-2xl" />
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
      <Shimmer className="h-12 rounded-xl" />
      <Shimmer className="h-12 rounded-xl" />
      <Shimmer className="h-12 rounded-xl" />
      <Shimmer className="h-12 rounded-xl" />
    </div>
  </div>
);
