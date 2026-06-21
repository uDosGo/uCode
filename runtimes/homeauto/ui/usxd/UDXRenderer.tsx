/**
 * UDX (Universal Display eXtended) Renderer
 *
 * Renders USX UDX content as a retro terminal/teletext display.
 * Supports 40x24 grid with green/amber/cyan/white palettes.
 */

import React from 'react';

// ── Types ──────────────────────────────────────────────────────────

export interface UDXTheme {
  grid: string;       // e.g. "40x24"
  font: 'Teletext50' | 'Teletext50 Extended' | 'Teletext50 Condensed';
  palette: 'green' | 'amber' | 'cyan' | 'white';
  content: string[];
}

// ── Palette Map ────────────────────────────────────────────────────

const PALETTES: Record<string, { text: string; bg: string; accent: string; dim: string }> = {
  green: { text: '#33ff33', bg: '#001a00', accent: '#00cc00', dim: '#004d00' },
  amber:  { text: '#ffb000', bg: '#1a0f00', accent: '#cc8800', dim: '#4d3300' },
  cyan:   { text: '#00cccc', bg: '#001a1a', accent: '#009999', dim: '#004d4d' },
  white:  { text: '#cccccc', bg: '#1a1a1a', accent: '#999999', dim: '#4d4d4d' },
};

// ── UDX Renderer ───────────────────────────────────────────────────

export function UDXRenderer({ theme }: { theme: UDXTheme }) {
  const palette = PALETTES[theme.palette] || PALETTES.green;
  const [cols, rows] = (theme.grid || '40x24').split('x').map(Number);
  const content = theme.content || [];

  // Pad or truncate content to fit the grid
  const displayLines = content.slice(0, rows);
  while (displayLines.length < rows) {
    displayLines.push('');
  }

  return (
    <div
      className="udx-terminal"
      style={{
        backgroundColor: palette.bg,
        color: palette.text,
        fontFamily: '"Courier New", "VT323", "Fira Code", monospace',
        fontSize: '14px',
        lineHeight: '1.4',
        padding: '16px',
        borderRadius: '12px',
        border: `1px solid ${palette.dim}`,
        boxShadow: `inset 0 0 30px ${palette.dim}40, 0 0 20px ${palette.dim}20`,
        overflow: 'hidden',
        maxWidth: '100%',
      }}
    >
      {/* Scanline overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          background: `repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            ${palette.bg}08 2px,
            ${palette.bg}08 4px
          )`,
          pointerEvents: 'none',
          borderRadius: '12px',
        }}
      />

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {displayLines.map((line, i) => (
          <div
            key={i}
            style={{
              whiteSpace: 'pre',
              letterSpacing: '0.5px',
              height: '1.4em',
              color: line.startsWith('┌') || line.startsWith('└') || line.startsWith('├')
                ? palette.accent
                : line.startsWith('│') && line.includes('[')
                  ? palette.text
                  : palette.text,
              opacity: line.trim() === '' ? 0.3 : 1,
            }}
          >
            {line || '\u00A0'}
          </div>
        ))}
      </div>

      {/* CRT glow effect */}
      <div
        style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          background: `radial-gradient(ellipse at center, transparent 60%, ${palette.bg}60 100%)`,
          pointerEvents: 'none',
          borderRadius: '12px',
        }}
      />
    </div>
  );
}

export default UDXRenderer;
