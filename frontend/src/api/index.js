import axios from 'axios';

const client = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8080',
  timeout: 10000
});

client.interceptors.request.use(config => {
  const token = localStorage.getItem('jwt');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default {
  health() {
    return client.get('/api/health');
  },
  listDatasets() {
    return client.get('/api/datasets');
  },
  listFiles(datasetId) {
    return client.get(`/api/datasets/${datasetId}/files`);
  },
  createFile(datasetId, payload) {
    return client.post(`/api/datasets/${datasetId}/files`, payload);
  },
  getDownloadUrl(fileId) {
    return client.get(`/api/files/${fileId}/download-url`);
  },
  listMetrics(params) {
    return client.get('/api/metrics', { params });
  },
  listReports(params) {
    return client.get('/api/reports', { params });
  },
  createReport(payload) {
    return client.post('/api/reports', payload);
  },
  login(payload) {
    return client.post('/api/auth/login', payload);
  },
  createUploadUrl(params) {
    return client.post('/api/files/upload-url', null, { params });
  }
};
