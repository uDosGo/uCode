/**
 * HomeNest Surface — USX/UDO/UDX Surface Component
 *
 * Follows the Groovebox surface pattern:
 * - Fetches USX files from the uHome server API
 * - Renders UDO (rich UI) or UDX (terminal) views
 * - Handles navigation between surfaces
 * - Dispatches custom events for USXD integration
 */

import React, { useState, useEffect, useCallback } from 'react';
import { UDORenderer, UDOTheme } from '../../ui/usxd/UDORenderer';
import { UDXRenderer, UDXTheme } from '../../ui/usxd/UDXRenderer';

// ── Types ──────────────────────────────────────────────────────────

type ViewMode = 'udo' | 'udx';
type SurfacePage = 'dashboard' | 'media' | 'automation';

interface USXFile {
  meta: {
    title: string;
    description: string;
    surface: 'udo' | 'udx' | 'both';
    version: string;
  };
  udo?: UDOTheme;
  udx?: UDXTheme;
  actions?: {
    on_load?: USXAction[];
    on_select?: USXAction[];
    on_timer?: TimedAction[];
  };
}

interface USXAction {
  type: string;
  command: string;
  parameters?: Record<string, unknown>;
}

interface TimedAction {
  delay: number;
  action: USXAction;
}

// ── Constants ──────────────────────────────────────────────────────

const API_BASE = '';
const SURFACE_PAGES: { id: SurfacePage; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '🏠' },
  { id: 'media', label: 'Media', icon: '🎬' },
  { id: 'automation', label: 'Automation', icon: '⚡' },
];

// ── Helpers ────────────────────────────────────────────────────────

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Accept': 'application/json' },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

// ── HomeNest Surface ───────────────────────────────────────────────

export function HomeNestSurface() {
  const [page, setPage] = useState<SurfacePage>('dashboard');
  const [viewMode, setViewMode] = useState<ViewMode>('udo');
  const [usx, setUsx] = useState<USXFile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadUSX = useCallback(async (name: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchJson<USXFile>(`/api/usx/${name}`);
      setUsx(data);
      // Auto-select view mode based on USX surface type
      if (data.meta.surface === 'udx') setViewMode('udx');
      else if (data.meta.surface === 'udo') setViewMode('udo');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load USX');
      setUsx(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load initial USX
  useEffect(() => {
    loadUSX(page);
  }, [page, loadUSX]);

  // Handle USX timer actions
  useEffect(() => {
    if (!usx?.actions?.on_timer) return;
    const timers = usx.actions.on_timer.map(({ delay, action }) =>
      setInterval(() => {
        console.log('[HomeNest] Timer action:', action.type, action.command);
        // Re-fetch the USX to refresh data
        loadUSX(page);
      }, delay)
    );
    return () => timers.forEach(clearInterval);
  }, [usx, page, loadUSX]);

  // Handle UDO action events
  useEffect(() => {
    const handler = (e: CustomEvent) => {
      const { type, command } = e.detail;
      console.log('[HomeNest] UDO action:', type, command);
      if (type === 'navigate') {
        const target = SURFACE_PAGES.find(p => p.id === command);
        if (target) setPage(target.id);
      }
    };
    window.addEventListener('udo:action', handler as EventListener);
    return () => window.removeEventListener('udo:action', handler as EventListener);
  }, []);

  const handleNavigate = useCallback((target: string) => {
    if (target === 'home') {
      window.dispatchEvent(new CustomEvent('homenest:navigate', { detail: { target: 'home' } }));
    } else {
      const found = SURFACE_PAGES.find(p => p.id === target);
      if (found) setPage(found.id);
    }
  }, []);

  return (
    <div className="homenest-surface min-h-screen bg-gray-900 text-gray-100">
      {/* Navigation */}
      <header className="homenest-nav border-b border-gray-800 bg-gray-900/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => handleNavigate('home')}
              className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
              title="Back to UI Hub"
              aria-label="Back to UI Hub"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </button>
            <span className="text-lg font-semibold text-purple-400">HomeNest</span>
          </div>

          <nav className="flex items-center gap-1" aria-label="Pages">
            {SURFACE_PAGES.map(p => (
              <button
                key={p.id}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  page === p.id
                    ? 'bg-purple-600/20 text-purple-300 border border-purple-600/30'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                }`}
                onClick={() => handleNavigate(p.id)}
              >
                <span className="mr-1.5">{p.icon}</span>
                {p.label}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <button
              className={`px-2 py-1 rounded text-xs font-mono transition-colors ${
                viewMode === 'udo'
                  ? 'bg-blue-600/20 text-blue-300 border border-blue-600/30'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
              onClick={() => setViewMode('udo')}
            >
              UDO
            </button>
            <button
              className={`px-2 py-1 rounded text-xs font-mono transition-colors ${
                viewMode === 'udx'
                  ? 'bg-green-600/20 text-green-300 border border-green-600/30'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
              onClick={() => setViewMode('udx')}
            >
              UDX
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400" />
            <span className="ml-3 text-gray-400">Loading {page}...</span>
          </div>
        )}

        {error && (
          <div className="p-6 rounded-xl bg-red-900/20 border border-red-800/30 text-center">
            <p className="text-red-300 mb-2">Failed to load surface</p>
            <p className="text-red-400/70 text-sm">{error}</p>
            <button
              className="mt-4 px-4 py-2 rounded-lg bg-red-800/30 text-red-300 text-sm hover:bg-red-800/50 transition-colors"
              onClick={() => loadUSX(page)}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && usx && (
          <div>
            {/* Surface meta info */}
            <div className="mb-4 text-center">
              <p className="text-xs text-gray-500 font-mono">
                {usx.meta.title} v{usx.meta.version} · {usx.meta.surface.toUpperCase()} surface
              </p>
            </div>

            {/* Renderer */}
            {viewMode === 'udo' && usx.udo && (
              <UDORenderer theme={usx.udo} />
            )}
            {viewMode === 'udx' && usx.udx && (
              <div className="max-w-lg mx-auto">
                <UDXRenderer theme={usx.udx} />
              </div>
            )}

            {/* Fallback if selected view mode isn't available */}
            {viewMode === 'udo' && !usx.udo && usx.udx && (
              <div className="text-center py-8">
                <p className="text-gray-400 mb-2">UDO view not available for this surface</p>
                <button
                  className="px-4 py-2 rounded-lg bg-green-800/30 text-green-300 text-sm hover:bg-green-800/50 transition-colors"
                  onClick={() => setViewMode('udx')}
                >
                  Switch to UDX view
                </button>
              </div>
            )}
            {viewMode === 'udx' && !usx.udx && usx.udo && (
              <div className="text-center py-8">
                <p className="text-gray-400 mb-2">UDX view not available for this surface</p>
                <button
                  className="px-4 py-2 rounded-lg bg-blue-800/30 text-blue-300 text-sm hover:bg-blue-800/50 transition-colors"
                  onClick={() => setViewMode('udo')}
                >
                  Switch to UDO view
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-4 text-center text-xs text-gray-600">
        <p>HomeNest Surface · USX v1.0.0 · uDos HomeNest</p>
      </footer>
    </div>
  );
}

export default HomeNestSurface;
