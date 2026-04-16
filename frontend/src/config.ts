export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/translate'
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const HEALTH_URL = `${API_URL}/health`
export const LATENCY_URL = `${API_URL}/api/latency`
