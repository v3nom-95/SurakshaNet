'use client';

import React from 'react';
import { ShieldAlert, Zap, User, Activity } from 'lucide-react';

interface ClaimsTableProps {
    claims: any[];
    onSearch?: (query: string) => void;
    searchQuery?: string;
}

const ClaimsTable: React.FC<ClaimsTableProps> = ({ claims, onSearch, searchQuery }) => {
    return (
        <div className="fade-in">
            <header style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Security Anomalies</h1>
                    <p style={{ color: '#64748b' }}>Detected fraudulent patterns and ML-identified outliers</p>
                </div>
                <div style={{ position: 'relative', width: '300px' }}>
                    <div style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }}>
                        <Zap size={16} />
                    </div>
                    <input
                        type="text"
                        placeholder="Search Claim or Patient ID..."
                        value={searchQuery}
                        onChange={(e) => onSearch?.(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '0.6rem 1rem 0.6rem 2.5rem',
                            borderRadius: '10px',
                            border: '1px solid var(--card-border)',
                            fontSize: '0.875rem',
                            outline: 'none',
                            background: 'white'
                        }}
                    />
                </div>
            </header>

            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div className="data-table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Incident ID</th>
                                <th>Procedure</th>
                                <th>Amount</th>
                                <th>ML Confidence</th>
                                <th>Risk Score</th>
                                <th>Detection Flags</th>
                            </tr>
                        </thead>
                        <tbody>
                            {claims.length > 0 ? claims.map((c, i) => (
                                <tr key={`${c.claim_id}-${i}`}>
                                    <td>
                                        <div style={{ fontWeight: 600, color: 'var(--foreground)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <Activity size={14} color="var(--primary)" />
                                            {c.claim_id}
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginLeft: '1.25rem' }}>Patient: {c.patient_id}</div>
                                    </td>
                                    <td>
                                        <div style={{ fontWeight: 500 }}>{c.procedure_code}</div>
                                    </td>
                                    <td style={{ fontWeight: 700, color: 'var(--foreground)' }}>₹{c.claim_amount.toLocaleString()}</td>
                                    <td>
                                        <div style={{
                                            color: c.anomaly_score > 0.7 ? 'var(--danger)' : 'var(--accent)',
                                            fontWeight: 600,
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '0.4rem'
                                        }}>
                                            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: c.anomaly_score > 0.7 ? 'var(--danger)' : 'var(--accent)' }}></div>
                                            {(c.anomaly_score * 100).toFixed(1)}%
                                        </div>
                                    </td>
                                    <td>
                                        <div style={{
                                            fontWeight: 700,
                                            color: getRiskColor(c.risk_score),
                                            fontSize: '1rem'
                                        }}>
                                            {c.risk_score.toFixed(0)}
                                        </div>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            {c.rule_upcoding && <span title="Up-coding" style={{ background: '#eff6ff', color: '#2563eb', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>UP-CODE</span>}
                                            {c.rule_ghost_billing && <span title="Ghost Billing" style={{ background: '#fee2e2', color: '#ef4444', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>GHOST</span>}
                                            {c.rule_claim_surge && <span title="Claim Surge" style={{ background: '#fff7ed', color: '#f59e0b', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>SURGE</span>}
                                        </div>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
                                        No anomalous claims detected in this range
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

const getRiskColor = (score: number) => {
    if (score > 66) return 'var(--danger)';
    if (score > 33) return 'var(--accent)';
    return 'var(--success)';
};

export default ClaimsTable;
