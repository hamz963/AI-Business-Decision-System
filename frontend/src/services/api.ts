import axios from 'axios';
import { 
  ExecutiveDashboardData, Dataset, ScenarioParams, 
  ScenarioResult, Decision, AIAnalystResponse, ForecastResult, AnomalyItem, ModelOption 
} from '../types';

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ai_bdss_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentication APIs
export const authApi = {
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    localStorage.setItem('ai_bdss_token', res.data.access_token);
    return res.data;
  },
  register: async (data: any) => {
    const res = await api.post('/auth/register', data);
    localStorage.setItem('ai_bdss_token', res.data.access_token);
    return res.data;
  },
  getMe: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },
  logout: () => {
    localStorage.removeItem('ai_bdss_token');
  }
};

// Executive Dashboard APIs
export const dashboardApi = {
  getExecutive: async (datasetId?: string): Promise<ExecutiveDashboardData> => {
    const res = await api.get('/dashboard/executive', {
      params: { dataset_id: datasetId }
    });
    return res.data;
  }
};

// Dataset APIs
export const datasetsApi = {
  list: async (): Promise<Dataset[]> => {
    const res = await api.get('/datasets');
    return res.data;
  },
  upload: async (formData: FormData): Promise<Dataset> => {
    const res = await api.post('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },
  getPreview: async (datasetId: string, limit: number = 50) => {
    const res = await api.get(`/datasets/${datasetId}/preview`, {
      params: { limit }
    });
    return res.data;
  },
  delete: async (datasetId: string) => {
    await api.delete(`/datasets/${datasetId}`);
  }
};

// Scenario Simulator APIs
export const scenariosApi = {
  simulate: async (params: ScenarioParams, datasetId?: string): Promise<ScenarioResult> => {
    const res = await api.post('/scenarios/simulate', {
      parameters: params,
      dataset_id: datasetId,
      name: 'Custom What-If Run'
    });
    return res.data;
  },
  save: async (params: ScenarioParams, name: string, description?: string, datasetId?: string): Promise<ScenarioResult> => {
    const res = await api.post('/scenarios/save', {
      parameters: params,
      name,
      description,
      dataset_id: datasetId
    });
    return res.data;
  },
  list: async (): Promise<ScenarioResult[]> => {
    const res = await api.get('/scenarios');
    return res.data;
  }
};

// Decisions & Recommendations APIs
export const decisionsApi = {
  list: async (status?: string): Promise<Decision[]> => {
    const res = await api.get('/decisions', { params: { status } });
    return res.data;
  },
  review: async (decisionId: string, status: 'approved' | 'rejected' | 'implemented', notes?: string): Promise<Decision> => {
    const res = await api.post(`/decisions/${decisionId}/review`, {
      status,
      review_notes: notes
    });
    return res.data;
  },
  create: async (data: any): Promise<Decision> => {
    const res = await api.post('/decisions', data);
    return res.data;
  }
};

// AI Analyst APIs
export const aiAnalystApi = {
  getModels: async (): Promise<ModelOption[]> => {
    const res = await api.get('/ai/models');
    return res.data;
  },
  selectModel: async (modelId: string): Promise<{ status: string; active_model: string }> => {
    const res = await api.post('/ai/models/select', { model_id: modelId });
    return res.data;
  },
  query: async (queryText: string, datasetId?: string, modelName?: string): Promise<AIAnalystResponse> => {
    const res = await api.post('/ai/query', {
      query: queryText,
      dataset_id: datasetId,
      model_name: modelName
    });
    return res.data;
  }
};

// Analytics & Forecasting APIs
export const analyticsApi = {
  getForecast: async (datasetId?: string, periodsAhead: number = 6): Promise<ForecastResult> => {
    const res = await api.get('/analytics/forecast', {
      params: { dataset_id: datasetId, periods_ahead: periodsAhead }
    });
    return res.data;
  },
  getAnomalies: async (datasetId?: string, zThreshold: number = 2.5): Promise<AnomalyItem[]> => {
    const res = await api.get('/analytics/anomalies', {
      params: { dataset_id: datasetId, z_threshold: zThreshold }
    });
    return res.data;
  }
};

// Reports APIs
export const reportsApi = {
  downloadMarkdown: () => {
    window.open('/api/v1/reports/export/markdown', '_blank');
  }
};
