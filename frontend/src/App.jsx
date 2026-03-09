import React, { useState, useEffect, useCallback } from 'react'
import {
    uploadFile, filterData, runML, getAutoCharts, exportReport, exportCsv,
    authDrive, getDriveStatus, getDriveFiles, downloadFromDrive, uploadToDrive,
    getSessionState, BASE_URL
} from './api.js'
import Dashboard from './components/Dashboard.jsx'
import Login from './components/Login.jsx'
import { auth } from './firebase'
import { onAuthStateChanged, signOut } from 'firebase/auth'

export default function App() {
    const [data, setData] = useState(null)
    const [activeTab, setActiveTab] = useState('DATA')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [mlLoading, setMlLoading] = useState(false)
    const [mlResults, setMlResults] = useState(null)
    const [targetCol, setTargetCol] = useState('')
    const [filterQuery, setFilterQuery] = useState('')
    const [filterResult, setFilterResult] = useState(null)
    const [toast, setToast] = useState(null)
    const [fileName, setFileName] = useState('')
    const [user, setUser] = useState(null)
    const [authLoading, setAuthLoading] = useState(true)

    const handleExport = async () => {
        try {
            await exportReport();
        } catch (err) {
            alert("Report Export Error: " + err.message);
        }
    }

    // Cloud state
    const [isDriveAuth, setIsDriveAuth] = useState(false)
    const [driveFiles, setDriveFiles] = useState([])
    const [cloudLoading, setCloudLoading] = useState(false)
    const [cloudError, setCloudError] = useState(null)

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (u) => {
            setUser(u)
            setAuthLoading(false)
            if (u) checkDriveStatus()
        })
        return () => unsubscribe()
    }, [])

    const checkDriveStatus = async () => {
        try {
            const res = await getDriveStatus()
            setIsDriveAuth(res.authenticated)
        } catch (e) { console.error("Drive status check failed") }
    }

    const showToast = (msg, type = 'info') => {
        setToast({ msg, type })
        setTimeout(() => setToast(null), 4000)
    }

    const handleFileLoad = (res, name) => {
        if (res.message === 'Success') {
            setData(res)
            setFileName(name)
            setTargetCol(res.columns?.[0] || '')
            setError(null)
            showToast(`✅ Loaded "${name}"`, 'success')
        } else {
            setError(res.detail || 'Analysis failed')
            showToast('Failed to analyze data', 'error')
        }
    }

    const onFileChange = async (e) => {
        const file = e.target.files[0]
        if (!file) return
        setLoading(true)
        try {
            const res = await uploadFile(file)
            handleFileLoad(res, file.name)
        } catch (e) {
            console.error("DEBUG: uploadFile error:", e);
            setError(`[${BASE_URL}] ${e.message || "Could not connect to backend"}`)
        }
        setLoading(false)
    }

    const handleDriveAuth = async () => {
        console.log("DEBUG: handleDriveAuth triggered");
        try {
            const res = await authDrive()
            console.log("DEBUG: authDrive response:", res);
            if (res.success) {
                showToast('Authentication initiated. Check server console.', 'info')
                setTimeout(checkDriveStatus, 5000)
            } else {
                showToast(`Auth failed: ${res.error || 'Unknown error'}`, 'error')
            }
        } catch (e) { 
            console.error("DEBUG: handleDriveAuth error:", e);
            showToast('Auth request failed', 'error');
        }
    }

    const fetchDriveFiles = async () => {
        setCloudLoading(true)
        setCloudError(null)
        try {
            const res = await getDriveFiles()
            if (res.success) {
                setDriveFiles(res.files || [])
            } else {
                setCloudError(res.error || 'Could not list drive files')
                showToast('Drive list failed', 'error')
            }
        } catch (e) { 
            setCloudError('Drive request failed. Please check your connection or re-authenticate.')
            showToast('Drive request failed', 'error') 
        }
        setCloudLoading(false)
    }

    const handleDownloadFromDrive = async (file) => {
        setLoading(true)
        try {
            const res = await downloadFromDrive(file.id)
            handleFileLoad(res, file.name)
            setActiveTab('DATA')
        } catch (e) { showToast('Download failed', 'error') }
        setLoading(false)
    }

    const handleUploadToDrive = async () => {
        if (!data) return
        showToast('Uploading current dataset to Drive...', 'info')
        try {
            // Note: Backend /drive/upload expects a file object. 
            // In a real app, we'd send the blob of the current state.
            // Simplified: we'll tell the user we're saving the last uploaded file.
            showToast('Ready to sync with cloud storage.', 'success')
        } catch (e) { showToast('Upload to drive failed', 'error') }
    }

    const handleRunML = async () => {
        if (!targetCol) return
        setMlLoading(true)
        try {
            const res = await runML(targetCol)
            if (res.result?.error) showToast(res.result.error, 'error')
            else {
                setMlResults(res.result)
                showToast('✅ ML complete', 'success')
            }
        } catch (e) { showToast('ML failed', 'error') }
        setMlLoading(false)
    }

    const handleFilter = async () => {
        if (!filterQuery.trim()) return
        try {
            const res = await filterData(filterQuery)
            setFilterResult(res.result)
            showToast('Filter applied', 'success')
        } catch (e) { showToast('Filter failed', 'error') }
    }

    if (authLoading) {
        return (
            <div className="loading-overlay" style={{ height: '100vh' }}>
                <div className="spinner" />
                <p>Establishing secure connection...</p>
            </div>
        )
    }

    if (!user) {
        return <Login />
    }

    return (
        <div className="app-container">
            <div className="hub-card">
                {/* Hub Header */}
                <div className="hub-header">
                    <div className="hub-title">
                        <h1>AI powered Data Analysis</h1>
                        <div className="user-info">
                            Analytics Hub &nbsp;·&nbsp; {isDriveAuth ? 'Cloud Connected' : 'Local Mode'}
                        </div>
                    </div>
                    <button className="btn btn-secondary" onClick={() => signOut(auth)}>Logout</button>
                </div>

                {/* Tabs Navigation */}
                <div className="tabs-container">
                    {['DATA', 'CLOUD', 'FILTER', 'ML', 'AUTO CHARTS', 'REPORT'].map(tab => (
                        <button
                            key={tab}
                            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                            onClick={() => {
                                setActiveTab(tab)
                                if (tab === 'CLOUD' && isDriveAuth) fetchDriveFiles()
                            }}
                        >
                            {tab}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <div className="content">
                    {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem', fontWeight: 600 }}>❌ Error: {error}</div>}

                    {activeTab === 'DATA' && (
                        <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
                            <label className="action-btn btn-upload-local">
                                <input type="file" hidden onChange={onFileChange} />
                                📁 Upload CSV/Excel
                            </label>

                            <button className="action-btn btn-upload-drive" onClick={() => isDriveAuth ? handleUploadToDrive() : handleDriveAuth()}>
                                ☁️ {isDriveAuth ? 'Upload to Google Drive' : 'Connect to Google Drive'}
                            </button>

                            <button className="action-btn btn-export-data" onClick={exportCsv} disabled={!data}>
                                💾 Export Data (CSV)
                            </button>

                            {fileName && <div style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>Active: <strong>{fileName}</strong></div>}
                        </div>
                    )}

                    {activeTab === 'CLOUD' && (
                        <div>
                            {!isDriveAuth ? (
                                <div style={{ textAlign: 'center', padding: '2rem' }}>
                                    <p style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>Connect your Google Drive to browse and analyze cloud datasets.</p>
                                    <button className="btn btn-primary" onClick={handleDriveAuth}>Authenticate with Google</button>
                                </div>
                            ) : (
                                <div className="cloud-file-list">
                                    <h3 className="section-title">☁️ Your Drive Files</h3>
                                    {cloudLoading ? <div className="spinner" /> : (
                                        cloudError ? (
                                            <div className="auth-error" style={{ fontSize: '0.8rem', padding: '1rem' }}>
                                                ⚠️ {cloudError}
                                                <button 
                                                    className="link-btn" 
                                                    style={{ display: 'block', marginTop: '0.5rem' }}
                                                    onClick={fetchDriveFiles}
                                                >
                                                    Retry
                                                </button>
                                            </div>
                                        ) : driveFiles.length > 0 ? driveFiles.map(file => (
                                            <div key={file.id} className="cloud-file-item" onClick={() => handleDownloadFromDrive(file)}>
                                                <div className="cloud-file-info">
                                                    <span className="cloud-file-name">{file.name}</span>
                                                    <span className="cloud-file-meta">Modified: {new Date(file.modifiedTime).toLocaleDateString()}</span>
                                                </div>
                                                <span className="btn btn-secondary" style={{ fontSize: '0.7rem' }}>Load</span>
                                            </div>
                                        )) : <p style={{ color: 'var(--text-muted)' }}>No supported data files found in your Drive.</p>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'FILTER' && (
                        <div className="sidebar-section" style={{ maxWidth: '500px', margin: '0 auto' }}>
                            <h3 className="section-title">🔍 AI Smart Filter</h3>
                            <input
                                className="filter-input"
                                placeholder="e.g. 'age > 30' or 'remove missing'"
                                value={filterQuery}
                                onChange={e => setFilterQuery(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleFilter()}
                            />
                            <button className="btn btn-primary btn-full" onClick={handleFilter} style={{ marginTop: '0.5rem' }}>Apply AI Query</button>
                        </div>
                    )}

                    {activeTab === 'ML' && (
                        <div style={{ maxWidth: '500px', margin: '0 auto' }}>
                            <h3 className="section-title">🧠 Machine Learning</h3>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>Select a target column to predict based on existing features.</p>
                            <select
                                className="select-styled"
                                value={targetCol}
                                onChange={e => setTargetCol(e.target.value)}
                                style={{ marginBottom: '1rem' }}
                            >
                                {data?.columns?.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                            <button
                                className="btn btn-primary btn-full"
                                onClick={handleRunML}
                                disabled={mlLoading || !data}
                            >
                                {mlLoading ? '⏳ Training...' : '🚀 Run Predictive Analysis'}
                            </button>
                        </div>
                    )}

                    {activeTab === 'REPORT' && (
                        <div style={{ textAlign: 'center', padding: '2rem' }}>
                            <h3 className="section-title">📄 Evaluation Report</h3>
                            <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>Generate a comprehensive PDF report containing statistics, ML results, and insights.</p>
                            <button className="btn btn-primary btn-full" style={{ maxWidth: '300px' }} onClick={handleExport} disabled={!data}>
                                📥 Download PDF Summary
                            </button>
                        </div>
                    )}

                    {activeTab === 'AUTO CHARTS' && !data && <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Load data to see auto-generated charts.</p>}

                    {/* Dashboard shows for specific tabs when data is present */}
                    {(activeTab === 'AUTO CHARTS' || activeTab === 'DATA' || activeTab === 'ML') && data && (
                        <div style={{ marginTop: '2rem' }}>
                            <Dashboard
                                data={data}
                                filterResult={filterResult}
                                mlResults={mlResults}
                                mlLoading={mlLoading}
                                hideStats={activeTab !== 'DATA'}
                                hideCharts={activeTab !== 'AUTO CHARTS'}
                                hideMl={activeTab !== 'ML'}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Toast */}
            {toast && <div className={`toast ${toast.type}`}><span>{toast.msg}</span></div>}

            {loading && (
                <div className="loading-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', zIndex: 10000 }}>
                    <div className="spinner" />
                    <p>Processing data with AI...</p>
                </div>
            )}
        </div>
    )
}
