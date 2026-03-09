export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
console.log("DEBUG: frontend initialized with BASE_URL:", BASE_URL);

// Localtunnel requires this header to bypass its landing page for API requests
const headers = {
    'Bypass-Tunnel-Reminder': 'true',
};

const request = async (url, options = {}) => {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...headers,
                ...options.headers,
            },
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            const msg = `Server error (${response.status}) at ${url}: ${errorText.substring(0, 50)}`;
            console.error(`DEBUG: ${msg}`);
            throw new Error(msg);
        }
        
        return await response.json();
    } catch (error) {
        const msg = `Connection failed at ${url}: ${error.message}`;
        console.error(`DEBUG: ${msg}`, error);
        throw new Error(msg);
    }
};

export const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(`${BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
    });
};

export const filterData = async (query) => {
    return request(`${BASE_URL}/filter?query=${encodeURIComponent(query)}`);
};

export const runML = async (target) => {
    return request(`${BASE_URL}/ml?target=${encodeURIComponent(target)}`);
};

export const getAutoCharts = async () => {
    return request(`${BASE_URL}/auto_charts`);
};

export const exportReport = async () => {
    try {
        const response = await fetch(`${BASE_URL}/export_report`, {
            method: 'GET',
            headers: {
                'Bypass-Tunnel-Reminder': 'true',
            },
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate report');
        }
        
        const blob = await response.blob();
        if (blob.type !== 'application/pdf') {
            const text = await blob.text();
            try {
                const json = JSON.parse(text);
                throw new Error(json.detail || 'Report is not a valid PDF');
            } catch (e) {
                throw new Error('Server returned an invalid file format');
            }
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "Analysis_Report.pdf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        return { success: true };
    } catch (error) {
        console.error('Export error:', error);
        throw error;
    }
};

export const exportCsv = () => {
    window.open(`${BASE_URL}/export_csv`, '_blank');
};

export const getDriveStatus = async () => {
    return request(`${BASE_URL}/drive/status`);
};

export const authDrive = async () => {
    console.log("DEBUG: Calling authDrive at", `${BASE_URL}/drive/auth`);
    return request(`${BASE_URL}/drive/auth`, { method: 'POST' });
};

export const getDriveFiles = async () => {
    return request(`${BASE_URL}/drive/files`);
};

export const downloadFromDrive = async (fileId) => {
    return request(`${BASE_URL}/drive/download/${fileId}`);
};

export const uploadToDrive = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(`${BASE_URL}/drive/upload`, {
        method: 'POST',
        body: formData,
    });
};

export const getSessionState = async () => {
    return request(`${BASE_URL}/session_state`);
};

