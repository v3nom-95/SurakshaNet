'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from '@/components/Sidebar';
import Dashboard from '@/components/Dashboard';
import HospitalsTable from '@/components/HospitalsTable';
import ClaimsTable from '@/components/ClaimsTable';
import ReportView from '@/components/ReportView';
import LoginForm from '@/components/LoginForm';
import { ShieldAlert, RefreshCw, Filter, LogOut, User as UserIcon } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<string | null>(null);
  const [summaryData, setSummaryData] = useState<any>(null);
  const [hospitals, setHospitals] = useState<any[]>([]);
  const [claims, setClaims] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter States
  const [filters, setFilters] = useState({
    state: 'All',
    district: 'All'
  });
  const [searchQuery, setSearchQuery] = useState('');

  // Master Data for Filters
  const [stateOptions, setStateOptions] = useState<string[]>([]);
  const [districtOptions, setDistrictOptions] = useState<string[]>([]);
  const [allHospitalData, setAllHospitalData] = useState<any[]>([]);

  useEffect(() => {
    const savedUser = localStorage.getItem('ayushguard_user');
    if (savedUser) {
      setIsLoggedIn(true);
      setUser(savedUser);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('ayushguard_user');
    setIsLoggedIn(false);
    setUser(null);
  };

  const fetchData = useCallback(async (isAuto = false) => {
    if (!isLoggedIn) return;
    if (!isAuto) setLoading(true);
    setError(null);
    try {
      const query = `state=${filters.state}&district=${filters.district}`;
      const [summaryResp, hospitalsResp, claimsResp] = await Promise.all([
        fetch(`http://localhost:8000/get-summary?${query}`),
        fetch(`http://localhost:8000/get-all-hospitals?${query}`),
        fetch(`http://localhost:8000/get-claim-anomalies?limit=50&${query}`)
      ]);

      if (!summaryResp.ok || !hospitalsResp.ok || !claimsResp.ok) {
        throw new Error("Backend synchronization failure");
      }

      const summary = await summaryResp.json();
      const hospitals = await hospitalsResp.json();
      const claims = await claimsResp.json();

      setSummaryData(summary);
      setHospitals(hospitals);
      setClaims(claims);

      if (stateOptions.length === 0) {
        const allResp = await fetch('http://localhost:8000/get-all-hospitals?state=All&district=All');
        const allData = await allResp.json();
        setAllHospitalData(allData);
        const states = Array.from(new Set(allData.map((h: any) => h.state))).sort() as string[];
        setStateOptions(states);
      }
    } catch (err: any) {
      console.error(err);
      if (!isAuto) setError("Security Node Offline. Reconnecting...");
    }
    setLoading(false);
  }, [filters, stateOptions.length, isLoggedIn]);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (activeTab !== 'claims') return;

    setLoading(true);
    try {
      const q = `query=${query}&state=${filters.state}&district=${filters.district}`;
      const resp = await fetch(`http://localhost:8000/get-claims-search?${q}`);
      const data = await resp.json();
      setClaims(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (isLoggedIn) {
      fetchData();

      // Real-time polling every 30 seconds
      const interval = setInterval(() => {
        fetchData(true);
      }, 30000);

      return () => clearInterval(interval);
    }
  }, [fetchData, isLoggedIn]);

  // Update district options when state changes
  useEffect(() => {
    if (filters.state === 'All') {
      setDistrictOptions([]);
      setFilters(prev => ({ ...prev, district: 'All' }));
    } else {
      const districts = Array.from(new Set(
        allHospitalData
          .filter((h: any) => h.state === filters.state)
          .map((h: any) => h.district)
      )).sort() as string[];
      setDistrictOptions(districts);
      // Reset district if it's not in the new state
      if (!districts.includes(filters.district) && filters.district !== 'All') {
        setFilters(prev => ({ ...prev, district: 'All' }));
      }
    }
  }, [filters.state, allHospitalData]);

  const renderContent = () => {
    if (loading && !summaryData) return (
      <div className="fade-in" style={{ display: 'flex', height: '60vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
        <RefreshCw className="spinner" size={40} color="var(--primary)" />
        <p style={{ color: '#64748b', fontWeight: 500 }}>Synchronizing Security Database...</p>
      </div>
    );

    if (error) return (
      <div className="fade-in" style={{ display: 'flex', height: '60vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1.5rem', textAlign: 'center' }}>
        <ShieldAlert size={48} color="var(--danger)" />
        <h2 style={{ fontWeight: 700 }}>Connection Interrupted</h2>
        <p style={{ color: '#64748b', maxWidth: '400px' }}>{error}</p>
        <button className="action-button" onClick={() => fetchData()}>Retry Now</button>
      </div>
    );

    switch (activeTab) {
      case 'overview': return <Dashboard data={summaryData} filters={filters} />;
      case 'hospitals': return <HospitalsTable hospitals={hospitals} />;
      case 'claims': return <ClaimsTable claims={claims} onSearch={handleSearch} searchQuery={searchQuery} />;
      case 'report': return <ReportView filters={filters} />;
      default: return <Dashboard data={summaryData} filters={filters} />;
    }
  };

  if (!isLoggedIn) {
    return <LoginForm onLogin={(u) => { setIsLoggedIn(true); setUser(u); }} />;
  }

  return (
    <div className="layout">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} user={user} onLogout={handleLogout} />

      <main className="main-content">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', background: 'white', padding: '1rem 2rem', borderRadius: '16px', border: '1px solid var(--card-border)', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
          <div className="filter-bar" style={{ marginBottom: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#64748b' }}>
              <Filter size={18} />
              <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>Region Filter:</span>
            </div>

            <select
              className="select-input"
              value={filters.state}
              onChange={(e) => setFilters(p => ({ ...p, state: e.target.value }))}
            >
              <option value="All">All States</option>
              {stateOptions.map(s => <option key={s} value={s}>{s}</option>)}
            </select>

            <select
              className="select-input"
              value={filters.district}
              disabled={filters.state === 'All'}
              onChange={(e) => setFilters(p => ({ ...p, district: e.target.value }))}
            >
              <option value="All">All Districts</option>
              {districtOptions.map(d => <option key={d} value={d}>{d}</option>)}
            </select>

            {loading && summaryData && <RefreshCw size={16} className="spinner" color="var(--primary)" />}
          </div>
        </header>

        {renderContent()}
      </main>
    </div>
  );
}
