import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const rabiesAPI = {
  // Get all alerts (optionally filter by municipality)
  getAlerts: async (municipality = null) => {
    try {
      const params = municipality ? { municipality } : {};
      const response = await api.get('/api/alerts', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      throw error;
    }
  },

  // Get municipality summaries
  getMunicipalities: async () => {
    try {
      const response = await api.get('/api/municipalities');
      return response.data;
    } catch (error) {
      console.error('Error fetching municipalities:', error);
      throw error;
    }
  },

  // Get barangay details
  getBarangayDetails: async (municipality, barangay) => {
    try {
      const response = await api.get(`/api/barangay/${municipality}/${barangay}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching barangay details:', error);
      throw error;
    }
  },

  // Get thresholds
  getThresholds: async () => {
    try {
      const response = await api.get('/api/thresholds');
      return response.data;
    } catch (error) {
      console.error('Error fetching thresholds:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};

export default api;
