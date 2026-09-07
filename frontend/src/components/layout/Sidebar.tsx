import React from 'react';
import { Target, Activity, Map as MapIcon, FileText, Settings, Database } from 'lucide-react';

interface SidebarProps {
  currentView: string;
  setCurrentView: (view: string) => void;
}

const navItems = [
  { id: 'mission', label: 'Mission', icon: Target },
  { id: 'analyze', label: 'Analyze', icon: Activity },
  { id: 'detections', label: 'Detections', icon: Database },
  { id: 'map', label: 'Survey Map', icon: MapIcon },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ currentView, setCurrentView }) => {
  return (
    <aside style={styles.sidebar}>
      <div style={styles.brand}>
        <div style={styles.logo}></div>
        <div>
          <h1 style={styles.title}>SONARIS</h1>
          <p style={styles.tagline}>Sonar Intelligence</p>
        </div>
      </div>
      
      <nav style={styles.nav}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              style={{ ...styles.navItem, ...(isActive ? styles.navItemActive : {}) }}
              onClick={() => setCurrentView(item.id)}
            >
              <Icon size={20} style={{ color: isActive ? 'var(--accent-cyan)' : 'var(--text-muted)' }} />
              <span style={styles.navLabel}>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={styles.footer}>
        <div style={styles.statusDot}></div>
        <span>SYSTEM ONLINE</span>
      </div>
    </aside>
  );
};

const styles: Record<string, React.CSSProperties> = {
  sidebar: {
    width: '250px',
    backgroundColor: 'var(--bg-panel)',
    borderRight: '1px solid var(--border-color)',
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
  },
  brand: {
    padding: '24px 20px',
    borderBottom: '1px solid var(--border-color)',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  logo: {
    width: '32px',
    height: '32px',
    backgroundColor: 'var(--accent-cyan)',
    borderRadius: '4px',
    boxShadow: '0 0 10px rgba(6, 182, 212, 0.5)',
  },
  title: {
    fontSize: '18px',
    fontWeight: 'bold',
    letterSpacing: '1px',
    color: 'var(--text-main)',
  },
  tagline: {
    fontSize: '11px',
    color: 'var(--accent-cyan)',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  nav: {
    flex: 1,
    padding: '20px 0',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '12px 24px',
    width: '100%',
    textAlign: 'left',
    color: 'var(--text-muted)',
    transition: 'all 0.2s',
  },
  navItemActive: {
    backgroundColor: 'rgba(6, 182, 212, 0.1)',
    color: 'var(--text-main)',
    borderRight: '3px solid var(--accent-cyan)',
  },
  navLabel: {
    fontSize: '14px',
    fontWeight: 500,
  },
  footer: {
    padding: '20px',
    borderTop: '1px solid var(--border-color)',
    fontSize: '11px',
    color: 'var(--accent-cyan)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontFamily: 'var(--font-mono)',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    backgroundColor: 'var(--accent-cyan)',
    borderRadius: '50%',
    boxShadow: '0 0 8px var(--accent-cyan)',
  }
};
