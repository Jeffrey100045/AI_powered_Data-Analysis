import React from 'react'
import {
    BarChart, Bar, LineChart, Line, ScatterChart, Scatter,
    PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']

function ChartRenderer({ chart }) {
    const type = chart.type
    const data = chart.data || []

    if (!data.length) return <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No data</p>

    const tooltipStyle = {
        backgroundColor: '#111827',
        border: '1px solid #1f2d45',
        borderRadius: '8px',
        color: '#f1f5f9',
        fontSize: '0.78rem'
    }

    if (type === 'Histogram' || type === 'Bar') {
        return (
            <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2d45" />
                    <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: '#fff' }} labelStyle={{ color: '#fff' }} />
                    <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]}>
                        {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        )
    }

    if (type === 'Scatter') {
        const xKey = chart.x
        const yKey = chart.y
        return (
            <ResponsiveContainer width="100%" height={220}>
                <ScatterChart margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2d45" />
                    <XAxis dataKey={xKey} name={xKey} tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} />
                    <YAxis dataKey={yKey} name={yKey} tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: '#fff' }} labelStyle={{ color: '#fff' }} cursor={{ fill: 'rgba(59,130,246,0.1)' }} />
                    <Scatter data={data} fill="#8b5cf6" />
                </ScatterChart>
            </ResponsiveContainer>
        )
    }

    if (type === 'Line') {
        const xKey = chart.x
        const yKey = chart.y
        return (
            <ResponsiveContainer width="100%" height={220}>
                <LineChart data={data} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2d45" />
                    <XAxis dataKey={xKey} tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} />
                    <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: '#fff' }} labelStyle={{ color: '#fff' }} />
                    <Line type="monotone" dataKey={yKey} stroke="#10b981" strokeWidth={2} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        )
    }

    if (type === 'Pie') {
        return (
            <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                    <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false} fontSize={10}>
                        {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: '#fff' }} labelStyle={{ color: '#fff' }} />
                </PieChart>
            </ResponsiveContainer>
        )
    }

    if (type === 'Heatmap') {
        const cols = chart.columns || []
        if (!cols.length) return null
        const getVal = (x, y) => {
            const item = data.find(d => d.x === x && d.y === y)
            return item ? item.value : 0
        }
        const getColor = (v) => {
            if (v >= 0.7) return '#10b981'
            if (v >= 0.3) return '#3b82f6'
            if (v >= 0) return '#94a3b8'
            if (v >= -0.3) return '#f59e0b'
            return '#ef4444'
        }
        return (
            <div style={{ overflowX: 'auto' }}>
                <table style={{ borderCollapse: 'collapse', fontSize: '0.7rem', width: '100%' }}>
                    <thead>
                        <tr>
                            <th style={{ padding: '4px', color: 'var(--text-muted)' }}></th>
                            {cols.map(c => <th key={c} style={{ padding: '4px 6px', color: 'var(--text-muted)', maxWidth: 60, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c}</th>)}
                        </tr>
                    </thead>
                    <tbody>
                        {cols.map(row => (
                            <tr key={row}>
                                <td style={{ padding: '4px 6px', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{row}</td>
                                {cols.map(col => {
                                    const v = getVal(row, col)
                                    return (
                                        <td key={col} title={`${row} vs ${col}: ${v}`} style={{
                                            padding: '6px',
                                            backgroundColor: getColor(v) + '33',
                                            border: '1px solid var(--border)',
                                            textAlign: 'center',
                                            color: getColor(v),
                                            fontWeight: 600
                                        }}>
                                            {v.toFixed(2)}
                                        </td>
                                    )
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        )
    }

    return <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Unsupported chart type: {type}</p>
}

function MLSection({ mlResults, mlLoading }) {
    if (mlLoading) {
        return (
            <div className="card">
                <div className="loading-overlay">
                    <div className="spinner" />
                    <p>Training and evaluating models…</p>
                </div>
            </div>
        )
    }

    if (!mlResults) return null

    const { task, target, winner, metric, comparison, plot_data, description, decision_adviser } = mlResults
    const maxScore = Math.max(...(comparison?.map(c => c.score) || [1]))

    return (
        <div>
            <div className="section-title">🧠 Machine Learning — {task} for <em style={{ color: 'var(--accent)' }}>{target}</em></div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                {/* Model Comparison */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">📊 Model Comparison</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{metric}</span>
                    </div>
                    <div className="ml-comparison">
                        {comparison?.map(m => (
                            <div key={m.model} className={`ml-model-row${m.model === winner?.model ? ' winner' : ''}`}>
                                <span className="ml-model-name">{m.model}</span>
                                <div className="ml-bar-container">
                                    <div className="ml-bar" style={{ width: `${(m.score / maxScore) * 100}%` }} />
                                </div>
                                <span className="ml-score">{(m.score * 100).toFixed(1)}%</span>
                                {m.model === winner?.model && <span className="winner-badge">Best</span>}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Pred vs Actual */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">📈 Actual vs Predicted</span>
                    </div>
                    {plot_data?.length > 0 ? (
                        <ResponsiveContainer width="100%" height={200}>
                            <ScatterChart margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1f2d45" />
                                <XAxis dataKey="actual" name="Actual" tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} />
                                <YAxis dataKey="predicted" name="Predicted" tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2d45', borderRadius: '8px', color: '#f1f5f9', fontSize: '0.78rem' }} itemStyle={{ color: '#fff' }} labelStyle={{ color: '#fff' }} />
                                <Scatter data={plot_data} fill="#10b981" />
                            </ScatterChart>
                        </ResponsiveContainer>
                    ) : <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No plot data</p>}
                </div>
            </div>

            {/* AI Insights */}
            {description && (
                <div className="ai-insight">
                    <strong>🤖 Model Explanation: </strong>
                    <span dangerouslySetInnerHTML={{ __html: description }} />
                </div>
            )}
            {decision_adviser && (
                <div className="ai-insight" style={{ marginTop: '0.75rem', borderColor: 'rgba(16,185,129,0.3)' }}>
                    <strong>💡 Decision Adviser: </strong>{decision_adviser}
                </div>
            )}
        </div>
    )
}

export default function Dashboard({ data, filterResult, mlResults, mlLoading, hideStats, hideCharts, hideMl }) {
    const { preview, columns, auto_charts } = data
    const displayData = filterResult && Array.isArray(filterResult) ? filterResult : preview

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            {/* Stats */}
            {!hideStats && (
                <div>
                    <div className="section-title">📋 Dataset Overview</div>
                    <div className="stats-grid" style={{ marginBottom: '1.25rem' }}>
                        <div className="stat-item">
                            <div className="stat-label">Rows</div>
                            <div className="stat-value">{preview?.length ?? '—'}</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-label">Columns</div>
                            <div className="stat-value">{columns?.length ?? '—'}</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-label">Charts</div>
                            <div className="stat-value">{auto_charts?.length ?? 0}</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-label">Status</div>
                            <div className="stat-value" style={{ color: 'var(--success)', fontSize: '0.8rem' }}>✅ Ready</div>
                        </div>
                    </div>

                    {/* Data Table */}
                    {displayData?.length > 0 && (
                        <div className="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        {Object.keys(displayData[0]).map(k => <th key={k}>{k}</th>)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {displayData.slice(0, 50).map((row, i) => (
                                        <tr key={i}>
                                            {Object.values(row).map((v, j) => (
                                                <td key={j} title={String(v ?? '')}>{v ?? '—'}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )
            }

            {/* Charts */}
            {
                !hideCharts && auto_charts?.length > 0 && (
                    <div>
                        <div className="section-title">📊 Auto-Generated Visualisations</div>
                        <div className="charts-grid">
                            {auto_charts.map((chart, i) => (
                                <div key={i} className="chart-card">
                                    <h4>{chart.type} — {chart.x}{chart.y ? ` vs ${chart.y}` : ''}</h4>
                                    <ChartRenderer chart={chart} />
                                    {chart.reason && (
                                        <div className="chart-reason">{chart.reason}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )
            }

            {/* ML */}
            {!hideMl && <MLSection mlResults={mlResults} mlLoading={mlLoading} />}
        </div >
    )
}
