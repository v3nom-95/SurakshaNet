'use client';

import React, { useState } from 'react';
import { FileText, Wand2, Download, CheckCircle2, AlertCircle, ShieldAlert, Activity } from 'lucide-react';

interface ReportViewProps {
    filters: {
        state: string;
        district: string;
    };
}

const ReportView: React.FC<ReportViewProps> = ({ filters }) => {
    const [reportText, setReportText] = useState('');
    const [blockchainTxId, setBlockchainTxId] = useState<string | null>(null);
    const [walletAddress, setWalletAddress] = useState<string | null>(null);
    const [quantumSeal, setQuantumSeal] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [generated, setGenerated] = useState(false);

    const generateReport = async () => {
        setIsLoading(true);
        try {
            const resp = await fetch(`http://localhost:8000/generate-report?state=${filters.state}&district=${filters.district}`);
            const data = await resp.json();
            console.log("Report Data Received:", data);
            setReportText(data.report_text);
            setBlockchainTxId(data.blockchain_tx_id);
            setWalletAddress(data.wallet_address);
            setQuantumSeal(data.quantum_seal);
            setGenerated(true);
        } catch (err) {
            console.error("Report Generation Error:", err);
        }
        setIsLoading(false);
    };

    return (
        <div className="fade-in">
            <header style={{ marginBottom: '1.5rem' }}>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>AI Audit Reports</h1>
                <p style={{ color: '#64748b' }}>Automated intelligence reports for regulatory compliance</p>
            </header>

            <div className="card" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
                {!generated ? (
                    <div style={{ maxWidth: '500px', margin: '0 auto' }}>
                        <div style={{ background: 'var(--primary-light)', width: '64px', height: '64px', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
                            <FileText size={32} color="var(--primary)" />
                        </div>
                        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.75rem' }}>Ready to Generate Report</h2>
                        <p style={{ color: '#64748b', marginBottom: '2.5rem' }}>
                            Our AI engine will analyze all anomalous patterns across {location.hostname} to produce a detailed compliance summary.
                        </p>
                        <button className="action-button" onClick={generateReport} disabled={isLoading} style={{ padding: '0.75rem 2rem' }}>
                            {isLoading ? (
                                <>
                                    <RefreshCwIcon />
                                    Analyzing Data...
                                </>
                            ) : (
                                <>
                                    <Wand2 size={18} />
                                    Run Audit Engine
                                </>
                            )}
                        </button>
                    </div>
                ) : (
                    <div style={{ textAlign: 'left' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', background: '#f0fdf4', padding: '1rem', borderRadius: '12px', border: '1px solid #dcfce7' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#16a34a' }}>
                                <CheckCircle2 size={24} />
                                <span style={{ fontWeight: 700 }}>Compliance Report Generated Successfully</span>
                            </div>
                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <button className="action-button" style={{ background: 'white', border: '1px solid var(--card-border)', color: 'var(--foreground)' }}>
                                    <Download size={16} /> PDF
                                </button>
                                <button className="action-button" onClick={() => setGenerated(false)}>
                                    New Report
                                </button>
                            </div>
                        </div>

                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            background: '#f8fafc',
                            padding: '0.75rem 1rem',
                            borderRadius: '12px',
                            border: '1px solid var(--card-border)',
                            marginBottom: '1.5rem',
                            fontSize: '0.8125rem'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--secondary)' }}>
                                <Activity size={16} />
                                <span style={{ fontWeight: 600 }}>Algorand Blockchain Securing Data</span>
                            </div>
                            <div style={{ color: '#64748b', display: 'flex', gap: '1rem' }}>
                                {blockchainTxId ? (
                                    <>
                                        <span>Wallet: <code style={{ color: 'var(--primary)', fontWeight: 600 }}>{walletAddress?.slice(0, 6)}...{walletAddress?.slice(-4)}</code></span>
                                        <span>TX: <a href={`https://testnet.explorer.perawallet.app/tx/${blockchainTxId}`} target="_blank" rel="noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>{blockchainTxId.slice(0, 10)}...</a></span>
                                    </>
                                ) : (
                                    <span style={{ color: 'var(--danger)' }}>Blockchain Node Communication Failure</span>
                                )}
                            </div>
                        </div>

                        {quantumSeal && (
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                background: '#f5f3ff', // subtle purple tint
                                padding: '0.75rem 1rem',
                                borderRadius: '12px',
                                border: '1px solid #ede9fe',
                                marginBottom: '1.5rem',
                                fontSize: '0.8125rem'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#7c3aed' }}>
                                    <ShieldAlert size={16} />
                                    <span style={{ fontWeight: 600 }}>Quantum Seal Active</span>
                                </div>
                                <div style={{ color: '#64748b', display: 'flex', gap: '1rem' }}>
                                    <span>Token: <code style={{ color: '#7c3aed', fontWeight: 600 }}>{quantumSeal.quantum_entropy_token?.slice(0, 12)}...</code></span>
                                    <span>Sig: <code style={{ color: '#7c3aed', fontWeight: 600 }}>{quantumSeal.seal_signature?.slice(0, 12)}...</code></span>
                                </div>
                            </div>
                        )}

                        <div style={{
                            background: '#f8fafc',
                            padding: '2rem',
                            borderRadius: '12px',
                            border: '1px solid var(--card-border)',
                            maxHeight: '600px',
                            overflowY: 'auto',
                            boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)'
                        }}>
                            <pre style={{
                                whiteSpace: 'pre-wrap',
                                fontFamily: 'inherit',
                                fontSize: '0.9375rem',
                                lineHeight: '1.6',
                                color: '#334155'
                            }}>
                                {reportText}
                            </pre>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

const RefreshCwIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="spinner" style={{ marginRight: '8px' }}>
        <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
        <path d="M21 3v5h-5"></path>
        <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
        <path d="M3 21v-5h5"></path>
    </svg>
);

export default ReportView;
