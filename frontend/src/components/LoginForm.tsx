'use client';

import React, { useState } from 'react';
import { Lock, User, ShieldCheck, ArrowRight } from 'lucide-react';

interface LoginFormProps {
    onLogin: (username: string) => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                localStorage.setItem('ayushguard_user', data.username);
                onLogin(data.username);
            } else {
                setError(data.detail || 'Invalid username or password');
            }
        } catch (err) {
            setError('Connection to security server failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#ffffff',
            backgroundImage: 'radial-gradient(circle at 0% 0%, rgba(37, 99, 235, 0.03) 0%, transparent 50%), radial-gradient(circle at 100% 100%, rgba(14, 165, 233, 0.03) 0%, transparent 50%)',
            fontFamily: 'inherit'
        }}>
            <div className="fade-in" style={{
                width: '100%',
                maxWidth: '440px',
                background: '#ffffff',
                borderRadius: '32px',
                border: '1px solid #f1f5f9',
                padding: '4rem 3rem',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05)'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                    <div style={{
                        width: '80px',
                        height: '80px',
                        margin: '0 auto 1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <img src="/logo.png" alt="SurakshaNet Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                    </div>
                    <h1 style={{ color: 'var(--foreground)', fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem', letterSpacing: '-0.03em' }}>SurakshaNet</h1>
                    <p style={{ color: '#64748b', fontSize: '0.9375rem', fontWeight: 500 }}>Healthcare Fraud Defense Protocol</p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                    <div style={{ position: 'relative' }}>
                        <div style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}>
                            <User size={20} />
                        </div>
                        <input
                            type="text"
                            placeholder="Authorized Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                background: '#f8fafc',
                                border: '2px solid #f1f5f9',
                                borderRadius: '16px',
                                padding: '0.875rem 1.25rem 0.875rem 3.5rem',
                                color: 'var(--foreground)',
                                fontSize: '1rem',
                                fontWeight: 500,
                                outline: 'none',
                                transition: 'all 0.2s'
                            }}
                            onFocus={(e) => {
                                e.target.style.borderColor = 'var(--primary)';
                                e.target.style.background = 'white';
                                e.target.style.boxShadow = '0 0 0 4px var(--primary-glow)';
                            }}
                            onBlur={(e) => {
                                e.target.style.borderColor = '#f1f5f9';
                                e.target.style.background = '#f8fafc';
                                e.target.style.boxShadow = 'none';
                            }}
                        />
                    </div>

                    <div style={{ position: 'relative' }}>
                        <div style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }}>
                            <Lock size={20} />
                        </div>
                        <input
                            type="password"
                            placeholder="Security Protocol Key"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                background: '#f8fafc',
                                border: '2px solid #f1f5f9',
                                borderRadius: '16px',
                                padding: '0.875rem 1.25rem 0.875rem 3.5rem',
                                color: 'var(--foreground)',
                                fontSize: '1rem',
                                fontWeight: 500,
                                outline: 'none',
                                transition: 'all 0.2s'
                            }}
                            onFocus={(e) => {
                                e.target.style.borderColor = 'var(--primary)';
                                e.target.style.background = 'white';
                                e.target.style.boxShadow = '0 0 0 4px var(--primary-glow)';
                            }}
                            onBlur={(e) => {
                                e.target.style.borderColor = '#f1f5f9';
                                e.target.style.background = '#f8fafc';
                                e.target.style.boxShadow = 'none';
                            }}
                        />
                    </div>

                    {error && (
                        <div style={{
                            background: '#fef2f2',
                            border: '1px solid #fee2e2',
                            color: '#dc2626',
                            padding: '1rem',
                            borderRadius: '12px',
                            fontSize: '0.875rem',
                            fontWeight: 600,
                            textAlign: 'center',
                            animation: 'bounce 0.5s ease-in-out'
                        }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="action-button"
                        style={{
                            width: '100%',
                            padding: '1rem',
                            marginTop: '0.5rem',
                            justifyContent: 'center',
                            borderRadius: '16px',
                            fontSize: '1rem',
                            boxShadow: '0 10px 15px -3px rgba(37, 99, 235, 0.4)'
                        }}
                    >
                        {isLoading ? (
                            <div className="spinner" style={{ width: '20px', height: '20px', border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%' }}></div>
                        ) : (
                            <>
                                Initialize Session <ArrowRight size={20} />
                            </>
                        )}
                    </button>
                </form>

                <div style={{ marginTop: '2.5rem', textAlign: 'center' }}>
                    <p style={{ color: '#94a3b8', fontSize: '0.8125rem', fontWeight: 500 }}>
                        Ayushman Bharat Digital Health Security Stack v2.0
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginForm;
