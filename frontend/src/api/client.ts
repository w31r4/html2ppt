import axios, { AxiosError } from 'axios';

const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for LLM calls
});

// Types
export interface OutlineResponse {
  session_id: string;
  outline: string;
  status: 'draft' | 'confirmed' | 'generating' | 'completed' | 'error';
}

export interface SessionStatus {
  session_id: string;
  status: string;
  stage: string;
  progress: number;
  error?: string;
}

export interface GenerationResult {
  session_id: string;
  slides_md: string;
  components: Array<{
    name: string;
    code: string;
    section_title: string;
  }>;
  slides: Array<{
    frontmatter: Record<string, unknown>;
    content: string;
  }>;
}

export interface LLMSettings {
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
  base_url?: string;
}

// API Error handling
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function handleError(error: unknown): never {
  if (error instanceof AxiosError) {
    const message = error.response?.data?.detail || error.message;
    throw new ApiError(message, error.response?.status, error.response?.data?.detail);
  }
  throw error;
}

// API Functions
export async function submitRequirements(
  content: string,
  supplement?: string
): Promise<OutlineResponse> {
  try {
    const response = await apiClient.post<OutlineResponse>('/requirements', {
      content,
      supplement,
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function getOutline(sessionId: string): Promise<OutlineResponse> {
  try {
    const response = await apiClient.get<OutlineResponse>(`/outline/${sessionId}`);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function updateOutline(
  sessionId: string,
  outline: string
): Promise<OutlineResponse> {
  try {
    const response = await apiClient.put<OutlineResponse>(`/outline/${sessionId}`, {
      outline,
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function addSupplement(
  sessionId: string,
  content: string
): Promise<OutlineResponse> {
  try {
    const response = await apiClient.post<OutlineResponse>(
      `/outline/${sessionId}/supplement`,
      { content }
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function confirmOutline(sessionId: string): Promise<SessionStatus> {
  try {
    const response = await apiClient.post<SessionStatus>(
      `/outline/${sessionId}/confirm`
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function getGenerationStatus(sessionId: string): Promise<SessionStatus> {
  try {
    const response = await apiClient.get<SessionStatus>(
      `/generation/${sessionId}/status`
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function getResult(sessionId: string): Promise<GenerationResult> {
  try {
    const response = await apiClient.get<GenerationResult>(`/result/${sessionId}`);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export function getExportUrl(sessionId: string): string {
  return `${API_BASE_URL}/export/${sessionId}`;
}

export async function getLLMSettings(): Promise<LLMSettings> {
  try {
    const response = await apiClient.get<LLMSettings>('/settings/llm');
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function updateLLMSettings(settings: Partial<LLMSettings>): Promise<LLMSettings> {
  try {
    const response = await apiClient.put<LLMSettings>('/settings/llm', settings);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    await apiClient.get('/health');
    return true;
  } catch {
    return false;
  }
}

export default apiClient;