'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Loader2, AlertCircle, CheckCircle2, Link2, ChevronDown } from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'agent' | 'error';
  content: string;
  steps?: number;
  timestamp: string;
}

const SUGGESTED_QUERIES = [
  "Run the fraud pipeline and give me a full summary",
  "Who are the top 5 most suspicious hospitals?",
  "How many ghost billing cases are there in Maharashtra?",
  "Generate a full audit report and anchor it to Algorand blockchain",
  "Explain why the highest-risk claim is suspicious",
  "Show me the most suspicious claims in Delhi",
];

const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'agent',
      content: "Hello, I'm SurakshaNet — your Web3 fraud detection agent.\n\nI can analyse claims, identify suspicious hospitals, explain fraud patterns, generate audit reports, and anchor them immutably on the **Algorand blockchain** — all through natural language.\n\nWhat would you like to investigate?",
      timestamp: new Date().toLocaleTimeString(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentAvailable, setAgentAvailable] = useState<boolean | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    fetch(`${API}/agent/status`)
      .then(r => r.json())
      .then(data => setAgentAvailable(data.agent_available))
      .catch(() => setAgentAvailable(false));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (query?: string) => {
    const text = (query || input).trim();
    if (!text || isLoading) return;

    const userMsg: Message = {
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const resp = await fetch(`${API}/agent/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text }),
      });

      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.detail || 'Agent error');
      }

      setMessages(prev => [...prev, {
        role: data.status === 'error' ? 'error' : 'agent',
        content: data.status === 'error'
          ? (data.error || data.detail || 'Unknown error')
          : (data.answer || 'No response from agent'),
        steps: data.steps,
        timestamp: new Date().toLocaleTimeString(),
      }]);
    } catch (err: any) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: err.message || 'Failed to reach the agent. Is the backend running?',
        timestamp: new Date().toLocaleTimeString(),
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatContent = (content: string) => {
    // Render simple markdown-like formatting
    return content
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('**') && line.endsWith('**')) {
          return <p key={i} style={{ fontWeight: 700, marginBottom: '0.25rem' }}>{line.slice(2, -2)}</p>;
        }
        if (line.startsWith('- ')) {
          return <li key={i} style={{ marginLeft: '1rem', marginBottom: '0.2rem', listStyleType: 'disc' }}>{line.slice(2)}</li>;
        }
        if (line.trim() === '') return <br key={i} />;
        return <p key={i} style={{ marginBottom: '0.25rem' }}>{line}</p>;
      });
  };

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 180px)', minHeight: '500px' }}>
      {/* Header */}
      <header style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Web3 AI Agent</h1>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.375rem',
            background: agentAvailable ? '#f0fdf4' : '#fef2f2',
            border: `1px solid ${agentAvailable ? '#dcfce7' : '#fee2e2'}`,
            borderRadius: '999px',
            padding: '0.25rem 0.75rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: agentAvailable ? '#16a34a' : '#dc2626',
          }}>
            <div style={{
              width: '6px', height: '6px', borderRadius: '50%',
              background: agentAvailable ? '#16a34a' : '#dc2626',
              animation: agentAvailable ? 'pulse 2s infinite' : 'none',
            }} />
            {agentAvailable === null ? 'Checking...' : agentAvailable ? 'Agent Online · Gemini Flash' : 'GEMINI_API_KEY not set'}
          </div>
        </div>
        <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
          Powered by LangChain · Llama 3.3 70B via Groq (free) · Algorand TestNet
        </p>
      </header>

      {/* Suggested queries */}
      {messages.length <= 1 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
          {SUGGESTED_QUERIES.map((q, i) => (
            <button
              key={i}
              onClick={() => sendMessage(q)}
              disabled={isLoading || !agentAvailable}
              style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '999px',
                padding: '0.375rem 0.875rem',
                fontSize: '0.8125rem',
                fontWeight: 500,
                color: '#475569',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
              onMouseEnter={e => {
                (e.target as HTMLElement).style.background = 'var(--primary-light)';
                (e.target as HTMLElement).style.borderColor = 'var(--primary)';
                (e.target as HTMLElement).style.color = 'var(--primary)';
              }}
              onMouseLeave={e => {
                (e.target as HTMLElement).style.background = '#f8fafc';
                (e.target as HTMLElement).style.borderColor = '#e2e8f0';
                (e.target as HTMLElement).style.color = '#475569';
              }}
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Message thread */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        background: '#f8fafc',
        borderRadius: '16px',
        border: '1px solid var(--card-border)',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        marginBottom: '1rem',
      }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '0.75rem',
            flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
            alignItems: 'flex-start',
          }}>
            {/* Avatar */}
            <div style={{
              width: '36px', height: '36px', borderRadius: '50%', flexShrink: 0,
              background: msg.role === 'user' ? 'var(--primary)' : msg.role === 'error' ? '#fee2e2' : 'linear-gradient(135deg, #7c3aed, #2563eb)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {msg.role === 'user'
                ? <User size={18} color="white" />
                : msg.role === 'error'
                ? <AlertCircle size={18} color="#dc2626" />
                : <Bot size={18} color="white" />
              }
            </div>

            {/* Bubble */}
            <div style={{
              maxWidth: '78%',
              background: msg.role === 'user' ? 'var(--primary)' : msg.role === 'error' ? '#fef2f2' : 'white',
              color: msg.role === 'user' ? 'white' : msg.role === 'error' ? '#dc2626' : '#1e293b',
              borderRadius: msg.role === 'user' ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
              padding: '0.875rem 1.125rem',
              border: msg.role === 'error' ? '1px solid #fecaca' : '1px solid var(--card-border)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
              fontSize: '0.9375rem',
              lineHeight: 1.6,
            }}>
              <div>{formatContent(msg.content)}</div>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem',
                marginTop: '0.5rem',
                fontSize: '0.75rem',
                opacity: 0.6,
              }}>
                <span>{msg.timestamp}</span>
                {msg.steps !== undefined && msg.steps > 0 && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <CheckCircle2 size={12} />
                    {msg.steps} reasoning steps
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <div style={{
              width: '36px', height: '36px', borderRadius: '50%', flexShrink: 0,
              background: 'linear-gradient(135deg, #7c3aed, #2563eb)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Bot size={18} color="white" />
            </div>
            <div style={{
              background: 'white', border: '1px solid var(--card-border)',
              borderRadius: '4px 16px 16px 16px', padding: '0.875rem 1.125rem',
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              color: '#64748b', fontSize: '0.875rem',
            }}>
              <Loader2 size={16} className="spinner" />
              Agent is reasoning...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div style={{
        display: 'flex',
        gap: '0.75rem',
        background: 'white',
        border: '1px solid var(--card-border)',
        borderRadius: '16px',
        padding: '0.75rem 1rem',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
      }}>
        <textarea
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={agentAvailable ? "Ask the agent anything... (Shift+Enter for new line)" : "Set GEMINI_API_KEY in .env to enable the agent"}
          disabled={isLoading || !agentAvailable}
          rows={1}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            resize: 'none',
            fontSize: '0.9375rem',
            color: '#1e293b',
            fontFamily: 'inherit',
            lineHeight: 1.5,
            maxHeight: '120px',
            overflowY: 'auto',
          }}
        />
        <button
          onClick={() => sendMessage()}
          disabled={isLoading || !input.trim() || !agentAvailable}
          style={{
            width: '40px', height: '40px',
            background: input.trim() && agentAvailable ? 'var(--primary)' : '#e2e8f0',
            border: 'none', borderRadius: '12px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: input.trim() && agentAvailable ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s', flexShrink: 0,
          }}
        >
          <Send size={18} color={input.trim() && agentAvailable ? 'white' : '#94a3b8'} />
        </button>
      </div>

      {/* Footer note */}
      {!agentAvailable && agentAvailable !== null && (
        <p style={{ textAlign: 'center', fontSize: '0.8125rem', color: '#dc2626', marginTop: '0.5rem', fontWeight: 500 }}>
          Add <code style={{ background: '#fef2f2', padding: '0 4px', borderRadius: '4px' }}>GROQ_API_KEY=your_key</code> to .env —
          {' '}<a href="https://console.groq.com/" target="_blank" rel="noreferrer" style={{ color: '#dc2626', textDecoration: 'underline' }}>
            get a free key here
          </a>
        </p>
      )}
    </div>
  );
};

export default AgentChat;
