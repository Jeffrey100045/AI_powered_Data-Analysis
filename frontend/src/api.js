const BASE_URL = import.meta.env.VITE_API_URL || 'https://kavi-api-2026.loca.lt';

export const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
    });
    return response.json();
};

export const filterData = async (query) => {
    const response = await fetch(`${BASE_URL}/filter?query=${encodeURIComponent(query)}`);
    return response.json();
};

export const runML = async (target) => {
    const response = await fetch(`${BASE_URL}/ml?target=${encodeURIComponent(target)}`);
    return response.json();
};

export const getAutoCharts = async () => {
    const response = await fetch(`${BASE_URL}/auto_charts`);
    return response.json();
};

export const exportReport = () => {
    window.open(`${BASE_URL}/export_report`, '_blank');
};

export const exportCsv = () => {
    window.open(`${BASE_URL}/export_csv`, '_blank');
};

export const getDriveStatus = async () => {
    const response = await fetch(`${BASE_URL}/drive/status`);
    return response.json();
};

export const authDrive = async () => {
    const response = await fetch(`${BASE_URL}/drive/auth`, { method: 'POST' });
    return response.json();
};

export const getDriveFiles = async () => {
    const response = await fetch(`${BASE_URL}/drive/files`);
    return response.json();
};

export const downloadFromDrive = async (fileId) => {
    const response = await fetch(`${BASE_URL}/drive/download/${fileId}`);
    return response.json();
};

export const uploadToDrive = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${BASE_URL}/drive/upload`, {
        method: 'POST',
        body: formData,
    });
    return response.json();
};

export const getSessionState = async () => {
    const response = await fetch(`${BASE_URL}/session_state`);
    return response.json();
};

