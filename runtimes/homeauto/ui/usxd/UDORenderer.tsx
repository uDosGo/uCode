/**
 * UDO (Universal Display Object) Renderer
 *
 * Renders USX UDO components as React + Tailwind UI.
 * Supports: hero, grid, card, list, status, progress, badge, button
 */

import React from 'react';

// ── Types ──────────────────────────────────────────────────────────

export interface UDOComponent {
  type: 'hero' | 'grid' | 'card' | 'list' | 'status' | 'progress' | 'badge' | 'button';
  id?: string;
  title?: string;
  subtitle?: string;
  icon?: string;
  image?: string;
  color?: string;
  value?: string | number | boolean;
  progress?: number;
  status?: 'active' | 'inactive' | 'warning' | 'error' | 'success';
  columns?: number;
  items?: UDOItem[];
  onClick?: UDOAction;
}

export interface UDOItem {
  title?: string;
  subtitle?: string;
  label?: string;
  value?: string;
  icon?: string;
  color?: string;
  status?: string;
  onClick?: UDOAction;
}

export interface UDOAction {
  type: string;
  command: string;
  parameters?: Record<string, unknown>;
}

export interface UDOTheme {
  theme: 'dark' | 'light' | 'auto';
  layout: 'grid' | 'list' | 'carousel' | 'fullscreen';
  components: UDOComponent[];
}

// ── Icon Map ───────────────────────────────────────────────────────

const ICON_MAP: Record<string, string> = {
  home: '🏠', film: '🎬', tv: '📺', music: '🎵', play: '▶️',
  search: '🔍', settings: '⚙️', gear: '⚙️', zap: '⚡', sun: '☀️',
  moon: '🌙', activity: '📊', refresh: '🔄', calendar: '📅',
  check: '✅', radio: '📻', info: 'ℹ️', menu: '📋',
};

function icon(name?: string): string {
  return name ? ICON_MAP[name] || name : '';
}

// ── Status Color ───────────────────────────────────────────────────

function statusColor(status?: string): string {
  switch (status) {
    case 'active': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
    case 'success': return 'bg-green-500/20 text-green-300 border-green-500/30';
    case 'warning': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
    case 'error': return 'bg-red-500/20 text-red-300 border-red-500/30';
    default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
  }
}

function statusDot(status?: string): string {
  switch (status) {
    case 'active': return 'bg-blue-400';
    case 'success': return 'bg-green-400';
    case 'warning': return 'bg-yellow-400';
    case 'error': return 'bg-red-400';
    default: return 'bg-gray-400';
  }
}

// ── Component Renderers ────────────────────────────────────────────

function Hero({ comp }: { comp: UDOComponent }) {
  return (
    <div
      className="relative overflow-hidden rounded-2xl p-6 mb-6"
      style={{ background: `linear-gradient(135deg, ${comp.color || '#6750A4'} 0%, #1a1a2e 100%)` }}
    >
      <div className="flex items-center gap-4">
        <span className="text-4xl">{icon(comp.icon)}</span>
        <div>
          <h1 className="text-2xl font-bold text-white">{comp.title}</h1>
          {comp.subtitle && <p className="text-white/70 text-sm mt-1">{comp.subtitle}</p>}
        </div>
      </div>
      {comp.status && (
        <span className={`absolute top-3 right-3 px-2 py-0.5 rounded-full text-xs border ${statusColor(comp.status)}`}>
          {comp.status}
        </span>
      )}
    </div>
  );
}

function ActionGrid({ comp }: { comp: UDOComponent }) {
  const cols = comp.columns || 4;
  const gridCols = `grid-cols-${Math.min(cols, 4)}`;
  return (
    <div className="mb-6">
      {comp.title && <h2 className="text-lg font-semibold text-gray-200 mb-3">{comp.title}</h2>}
      <div className={`grid ${gridCols} gap-3`}>
        {(comp.items || []).map((item, i) => (
          <button
            key={i}
            className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gray-800/50 border border-gray-700/50 hover:bg-gray-700/50 hover:border-gray-600 transition-all cursor-pointer"
            onClick={() => handleAction(item.onClick)}
          >
            <span className="text-2xl">{icon(item.icon)}</span>
            <span className="text-sm font-medium text-gray-200">{item.title}</span>
            {item.subtitle && <span className="text-xs text-gray-400">{item.subtitle}</span>}
          </button>
        ))}
      </div>
    </div>
  );
}

function Card({ comp }: { comp: UDOComponent }) {
  return (
    <div
      className="mb-4 p-4 rounded-xl bg-gray-800/40 border border-gray-700/40 hover:border-gray-600/60 transition-all cursor-pointer"
      onClick={() => handleAction(comp.onClick)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon(comp.icon)}</span>
          <h3 className="font-medium text-gray-200">{comp.title}</h3>
        </div>
        {comp.status && <span className={`w-2 h-2 rounded-full ${statusDot(comp.status)}`} />}
      </div>
      {comp.subtitle && <p className="text-sm text-gray-400">{comp.subtitle}</p>}
      {comp.progress !== undefined && (
        <div className="mt-2">
          <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${comp.progress}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}

function StatusPanel({ comp }: { comp: UDOComponent }) {
  return (
    <div className="mb-6">
      {comp.title && <h2 className="text-lg font-semibold text-gray-200 mb-3">{comp.title}</h2>}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {(comp.items || []).map((item, i) => (
          <div key={i} className="p-3 rounded-lg bg-gray-800/30 border border-gray-700/30">
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-1.5 h-1.5 rounded-full ${statusDot(item.status)}`} />
              <span className="text-xs text-gray-400">{item.label}</span>
            </div>
            <span className="text-lg font-semibold text-gray-100">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProgressBar({ comp }: { comp: UDOComponent }) {
  return (
    <div className="mb-4 p-4 rounded-xl bg-gray-800/40 border border-gray-700/40">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="font-medium text-gray-200">{comp.title}</h3>
          {comp.value && <p className="text-sm text-gray-400">{comp.value}</p>}
        </div>
        {comp.status && <span className={`px-2 py-0.5 rounded-full text-xs border ${statusColor(comp.status)}`}>{comp.status}</span>}
      </div>
      <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${comp.progress || 0}%`, background: comp.color || '#3b82f6' }}
        />
      </div>
      <span className="text-xs text-gray-500 mt-1 block text-right">{comp.progress || 0}%</span>
    </div>
  );
}

function ListPanel({ comp }: { comp: UDOComponent }) {
  return (
    <div className="mb-6">
      {comp.title && <h2 className="text-lg font-semibold text-gray-200 mb-3">{comp.title}</h2>}
      <div className="space-y-1">
        {(comp.items || []).map((item, i) => (
          <div
            key={i}
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-800/30 transition-colors cursor-pointer"
            onClick={() => handleAction(item.onClick)}
          >
            <span className="text-lg">{icon(item.icon)}</span>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-200 truncate">{item.title}</div>
              {item.subtitle && <div className="text-xs text-gray-400 truncate">{item.subtitle}</div>}
            </div>
            {item.status && <span className={`w-1.5 h-1.5 rounded-full ${statusDot(item.status)}`} />}
          </div>
        ))}
      </div>
    </div>
  );
}

function Badge({ comp }: { comp: UDOComponent }) {
  return (
    <div
      className="mb-4 p-3 rounded-xl bg-gray-800/40 border border-gray-700/40 flex items-center justify-between cursor-pointer hover:bg-gray-800/60 transition-colors"
      onClick={() => handleAction(comp.onClick)}
    >
      <div className="flex items-center gap-2">
        <span className="text-lg">{icon(comp.icon)}</span>
        <span className="text-sm font-medium text-gray-200">{comp.title}</span>
      </div>
      <span className={`px-2 py-0.5 rounded-full text-xs border ${statusColor(comp.status)}`}>
        {comp.value}
      </span>
    </div>
  );
}

// ── Action Handler ─────────────────────────────────────────────────

function handleAction(action?: UDOAction) {
  if (!action) return;
  console.log('[UDO] Action:', action.type, action.command, action.parameters);
  // Dispatch custom event for the surface to handle
  window.dispatchEvent(new CustomEvent('udo:action', {
    detail: { type: action.type, command: action.command, parameters: action.parameters },
  }));
}

// ── Main Renderer ──────────────────────────────────────────────────

function renderComponent(comp: UDOComponent, index: number) {
  switch (comp.type) {
    case 'hero': return <Hero key={index} comp={comp} />;
    case 'grid': return <ActionGrid key={index} comp={comp} />;
    case 'card': return <Card key={index} comp={comp} />;
    case 'status': return <StatusPanel key={index} comp={comp} />;
    case 'progress': return <ProgressBar key={index} comp={comp} />;
    case 'list': return <ListPanel key={index} comp={comp} />;
    case 'badge': return <Badge key={index} comp={comp} />;
    default: return null;
  }
}

export function UDORenderer({ theme }: { theme: UDOTheme }) {
  const isDark = theme.theme === 'dark' || (theme.theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  return (
    <div className={`${isDark ? 'bg-gray-900 text-gray-100' : 'bg-gray-50 text-gray-900'} min-h-screen p-4 font-sans`}>
      <div className="max-w-4xl mx-auto">
        {theme.components.map((comp, i) => renderComponent(comp, i))}
      </div>
    </div>
  );
}

export default UDORenderer;
