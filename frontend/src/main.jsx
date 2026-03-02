import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Global Error Handler for Production Debugging
window.onerror = function (message, source, lineno, colno, error) {
    console.error("CRITICAL ERROR DETECTED:", message, "at", source, ":", lineno);
    const root = document.getElementById('root');
    if (root) {
        const isFirebaseError = message.includes('auth/invalid-api-key') || message.includes('apiKey');
        root.innerHTML = `
            <div style="padding: 40px; color: #f87171; background: #111827; min-height: 100vh; font-family: sans-serif;">
                <h1 style="font-size: 24px;">🚀 Application Setup Required</h1>
                <p style="color: #9ca3af; margin: 20px 0;">${message}</p>
                ${isFirebaseError ? `
                    <div style="border: 1px solid #374151; padding: 20px; border-radius: 8px; background: #1f2937;">
                        <h3 style="color: white; margin-top:0;">Likely Cause: Missing Firebase Keys</h3>
                        <p style="font-size: 14px;">Vite needs your Firebase keys <b>at build time</b>. </p>
                        <ol style="font-size: 14px; line-height: 1.6;">
                            <li>Go to Render Dashboard > kavi-frontend > Environment.</li>
                            <li>Ensure all VITE_FIREBASE_... variables are present.</li>
                            <li>Click "Manual Deploy" > <b>"Clear Build Cache and Deploy"</b>.</li>
                        </ol>
                    </div>
                ` : ''}
                <pre style="font-size: 10px; margin-top: 20px; color: #4b5563;">${source}:${lineno}</pre>
            </div>
        `;
    }
};

console.log("App Initializing... Environment Checked.");

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
