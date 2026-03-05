'use client';

import React, { useMemo } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, AreaChart, Area, Legend
} from 'recharts';
import { TrendingUp, Users, AlertTriangle, Activity } from 'lucide-react';

interface DashboardProps {
    data: any;
    filters: {
        state: string;
        district: string;
    };
}

const COLOR_MAP: { [key: string]: string } = {
    'Low': '#10b981',
    'Medium': '#f59e0b',
    'High': '#ef4444'
};

const Dashboard: React.FC<DashboardProps> = ({ data, filters }) => {
    if (!data) return <div className="fade-in">Loading security analytics...</div>;

    const { stats, monthly_trends, risk_distribution, hosp_type_risk, anomaly_type_counts } = data;

    return (
        <div className="fade-in">
            <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--foreground)', letterSpacing: '-0.03em' }}>
                        Security Protocol Analytics
                    </h1>
                    <p style={{ color: '#64748b', fontWeight: 500 }}>
                        Real-time threat monitoring of the Ayushman Bharat network
                        {filters.state === 'All' ? ' (National Level)' : ` - ${filters.state}`}
                    </p>
                </div>
                <div style={{ padding: '0.75rem 1.25rem', background: 'white', borderRadius: '12px', border: '1px solid var(--card-border)', display: 'flex', alignItems: 'center', gap: '0.75rem', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }}></div>
                    <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#0f172a' }}>Security Node Active</span>
                </div>
            </header>

            <div className="dashboard-grid">
                <KPICard
                    title="Claims Analyzed"
                    value={stats.total_claims.toLocaleString()}
                    trend="+8%"
                    icon={<Activity size={18} color="var(--primary)" />}
                />
                <KPICard
                    title="Flagged Anomalies"
                    value={stats.suspicious_claims.toLocaleString()}
                    trend="+2.4%"
                    isNegative
                    icon={<AlertTriangle size={18} color="var(--danger)" />}
                />
                <KPICard
                    title="Estimated Fraud Exposure"
                    value={stats.total_fraud_amount >= 10000000
                        ? `₹${(stats.total_fraud_amount / 10000000).toFixed(2)} Cr`
                        : `₹${(stats.total_fraud_amount / 100000).toFixed(2)} L`}
                    trend="+4.1%"
                    isNegative
                    icon={<TrendingUp size={18} color="var(--danger)" />}
                />
                <KPICard
                    title="Current Risk Rate"
                    value={`${(stats.suspicious_claims / (stats.total_claims || 1) * 100).toFixed(1)}%`}
                    trend="-0.8%"
                    icon={<Users size={18} color="var(--secondary)" />}
                />
            </div>

            <div className="charts-grid" style={{ gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
                <div className="card" style={{ border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.05)' }}>
                    <h3 className="section-title">Anomalous Activity Velocity</h3>
                    <div style={{ height: '320px', width: '100%' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={monthly_trends}>
                                <defs>
                                    <linearGradient id="colorSusp" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.15} />
                                        <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} dy={10} />
                                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} dx={-10} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                />
                                <Area type="monotone" dataKey="is_suspicious" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorSusp)" name="Flagged Incidents" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="card" style={{ border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.05)' }}>
                    <h3 className="section-title">System Risk Integrity</h3>
                    <div style={{ height: '320px', width: '100%' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={risk_distribution}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={70}
                                    outerRadius={100}
                                    paddingAngle={8}
                                    dataKey="count"
                                    nameKey="category"
                                    stroke="none"
                                >
                                    {risk_distribution.map((entry: any, index: number) => (
                                        <Cell key={`cell-${index}`} fill={COLOR_MAP[entry.category] || '#94a3b8'} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                />
                                <Legend verticalAlign="bottom" height={36} iconType="circle" />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="charts-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
                <div className="card" style={{ border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.05)' }}>
                    <h3 className="section-title">Anomalies by Classification</h3>
                    <div style={{ height: '300px', width: '100%' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={anomaly_type_counts} layout="vertical" margin={{ left: 40 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                                <XAxis type="number" stroke="#94a3b8" fontSize={11} axisLine={false} tickLine={false} />
                                <YAxis dataKey="type" type="category" stroke="#0f172a" fontSize={12} fontWeight={600} axisLine={false} tickLine={false} width={100} />
                                <Tooltip
                                    cursor={{ fill: '#f8fafc' }}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                />
                                <Bar dataKey="count" radius={[0, 8, 8, 0]} barSize={24}>
                                    {anomaly_type_counts.map((entry: any, index: number) => (
                                        <Cell key={`cell-${index}`} fill={index === 3 ? 'var(--primary)' : 'var(--danger)'} opacity={0.8} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="card" style={{ border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.05)' }}>
                    <h3 className="section-title">Facility Risk Breakdown</h3>
                    <div style={{ height: '300px', width: '100%' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={hosp_type_risk}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="hospital_type" stroke="#94a3b8" fontSize={11} axisLine={false} tickLine={false} dy={10} />
                                <YAxis stroke="#94a3b8" fontSize={11} axisLine={false} tickLine={false} dx={-10} />
                                <Tooltip
                                    cursor={{ fill: '#f8fafc' }}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                />
                                <Bar dataKey="avg_risk_score" name="Avg Risk Index" radius={[8, 8, 0, 0]} barSize={40}>
                                    {hosp_type_risk.map((entry: any, index: number) => (
                                        <Cell key={`cell-${index}`} fill={index % 2 === 0 ? 'var(--secondary)' : 'var(--accent)'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

const KPICard = ({ title, value, trend, icon, isNegative = false }: any) => (
    <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <div className="kpi-label">{title}</div>
            <div style={{ background: 'var(--primary-light)', padding: '0.4rem', borderRadius: '6px' }}>
                {icon}
            </div>
        </div>
        <div className="kpi-value">{value}</div>
        <div className={`kpi-trend ${isNegative ? 'trend-down' : 'trend-up'}`}>
            <span style={{ fontWeight: 600 }}>{trend}</span>
            <span style={{ color: '#94a3b8' }}>than last period</span>
        </div>
    </div>
);

export default Dashboard;
