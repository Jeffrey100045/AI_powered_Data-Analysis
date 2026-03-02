const BASE_URL = import.meta.env.VITE_API_URL || 'https://ai-daaas-api.loca.lt';

// Localtunnel requires this header to bypass its landing page for API requests
const headers = {
    'Bypass-Tunnel-Reminder': 'true',
};

const request = async (url, options = {}) => {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...headers,
            ...options.headers,
        },
    });
    return response.json();
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

export const exportReport = () => {
    window.open(`${BASE_URL}/export_report`, '_blank');
};

export const exportCsv = () => {
    window.open(`${BASE_URL}/export_csv`, '_blank');
};

export const getDriveStatus = async () => {
    return request(`${BASE_URL}/drive/status`);
};

export const authDrive = async () => {
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

