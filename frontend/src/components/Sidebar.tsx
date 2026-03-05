'use client';

import React from 'react';
import { LayoutDashboard, Hospital, AlertCircle, FileText, Settings, ShieldAlert, LogOut } from 'lucide-react';

interface SidebarProps {
    activeTab: string;
    setActiveTab: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps & { user: string | null; onLogout: () => void }> = ({ activeTab, setActiveTab, user, onLogout }) => {
    const menuItems = [
        { id: 'overview', icon: LayoutDashboard, label: 'Overview' },
        { id: 'hospitals', icon: Hospital, label: 'Hospital Risk' },
        { id: 'claims', icon: AlertCircle, label: 'Anomalies' },
        { id: 'report', icon: FileText, label: 'Reports' },
    ];

    return (
        <div className="top-nav">
            <div style={{ display: 'flex', alignItems: 'center', gap: '3rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <img src="/logo.png" alt="Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                    </div>
                    <span className="logo">
                        SurakshaNet
                    </span>
                </div>

                <nav className="nav-links">
                    {menuItems.map((item) => (
                        <div
                            key={item.id}
                            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(item.id)}
                            style={{ padding: '0.5rem 1rem' }}
                        >
                            <item.icon size={18} />
                            <span>{item.label}</span>
                        </div>
                    ))}
                </nav>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: '#f8fafc', padding: '0.5rem 1rem', borderRadius: '12px', border: '1px solid #f1f5f9' }}>
                    <div style={{ width: '8px', height: '8px', background: 'var(--success)', borderRadius: '50%', boxShadow: '0 0 8px var(--success)' }}></div>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: '#0f172a' }}>Node Active</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ textAlign: 'right' }}>
                        <p style={{ fontSize: '0.7rem', color: '#64748b', margin: 0, fontWeight: 600, textTransform: 'uppercase' }}>Admin Session</p>
                        <p style={{ fontSize: '0.875rem', fontWeight: 700, margin: 0, color: 'var(--foreground)' }}>{user}</p>
                    </div>
                    <button
                        onClick={onLogout}
                        style={{
                            background: '#fef2f2',
                            color: '#ef4444',
                            border: '1px solid #fee2e2',
                            padding: '0.6rem',
                            borderRadius: '12px',
                            cursor: 'pointer',
                            display: 'flex',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = '#fee2e2'}
                        title="Log Out"
                    >
                        <LogOut size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
