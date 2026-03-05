'use client';

import React from 'react';
import { Download, Filter, Search } from 'lucide-react';

interface HospitalsTableProps {
    hospitals: any[];
}

const HospitalsTable: React.FC<HospitalsTableProps> = ({ hospitals }) => {
    return (
        <div className="fade-in">
            <header style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Hospital Risk Index</h1>
                    <p style={{ color: '#64748b' }}>Comprehensive assessment of all healthcare facilities in the national database</p>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <button className="action-button" style={{ background: 'white', border: '1px solid var(--card-border)', color: 'var(--foreground)' }}>
                        <Download size={16} /> Export
                    </button>
                </div>
            </header>

            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div className="data-table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Healthcare Facility</th>
                                <th>Location</th>
                                <th>Claims</th>
                                <th>Risk Score</th>
                                <th>High Risk</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {hospitals.length > 0 ? hospitals.map((h, i) => (
                                <tr key={`${h.hospital_id}-${i}`}>
                                    <td>
                                        <div style={{ fontWeight: 600, color: 'var(--foreground)' }}>{h.hospital_name}</div>
                                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{h.hospital_id}</div>
                                    </td>
                                    <td>
                                        <div style={{ fontWeight: 500 }}>{h.state}</div>
                                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{h.district}</div>
                                    </td>
                                    <td style={{ fontWeight: 500 }}>{h.total_claims}</td>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                            <div style={{ flex: 1, minWidth: '80px', height: '6px', background: '#f1f5f9', borderRadius: '10px', overflow: 'hidden' }}>
                                                <div style={{ width: `${h.avg_risk_score}%`, height: '100%', background: getRiskColor(h.avg_risk_score), borderRadius: '10px' }}></div>
                                            </div>
                                            <span style={{ fontWeight: 600, fontSize: '0.8125rem', minWidth: '30px' }}>{h.avg_risk_score.toFixed(1)}</span>
                                        </div>
                                    </td>
                                    <td style={{ fontWeight: 500 }}>{h.high_risk_claims}</td>
                                    <td>
                                        <span className={`risk-tag risk-${h.risk_category_overall.toLowerCase()}`}>
                                            {h.risk_category_overall}
                                        </span>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
                                        No hospital data matches current filters
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

export default HospitalsTable;
