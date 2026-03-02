import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Global Error Handler for Production Debugging
window.onerror = function (message, source, lineno, colno, error) {
    console.error("CRITICAL ERROR DETECTED:", message, "at", source, ":", lineno);
    // Try to write to the DOM if possible
    const root = document.getElementById('root');
    if (root) {
        root.innerHTML = `<div style="padding: 20px; color: red;"><h1>App Crash</h1><p>${message}</p></div>`;
    }
};

console.log("App Initializing... Environment Checked.");

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
