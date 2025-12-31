import { defineStore } from 'pinia';

export type ThemeOption = 'light' | 'dark' | 'system';

export interface AppSettings {
  theme: ThemeOption;
  apiKey: string;
  baseUrl: string;
  defaultSlideCount: number;
  model: string;
  customModel: string;
  provider: string;
  isConfigured: boolean;
  verboseMode: boolean;
}

const SETTINGS_KEY = 'html2ppt_agent_settings';

export const useSettingsStore = defineStore('settings', {
  state: (): AppSettings => ({
    theme: 'system',
    apiKey: '',
    baseUrl: '',
    defaultSlideCount: 10,
    model: 'gpt-4o',
    customModel: '',
    provider: 'openai',
    isConfigured: false,
    verboseMode: false
  }),
  
  actions: {
    initSettings() {
      if (!import.meta.client) return;
      const raw = window.localStorage.getItem(SETTINGS_KEY);
      if (!raw) return;
      
      try {
        const parsed = JSON.parse(raw);
        this.$patch(parsed);
      } catch (e) {
        console.error('Failed to load settings', e);
      }
    },

    async fetchServerSettings() {
      const { request } = useApi();
      try {
        const response = await request<{
          provider: string;
          model: string;
          base_url: string | null;
          temperature: number;
          max_tokens: number;
          is_configured: boolean;
        }>('/settings/llm');
        this.provider = response.provider;
        this.model = response.model;
        this.baseUrl = response.base_url || '';
        this.isConfigured = response.is_configured;
      } catch (e) {
        console.error('Failed to load server settings', e);
      }
    },

    async saveLlmSettings(payload: { model: string; baseUrl?: string; apiKey?: string }) {
      const { request } = useApi();
      const body: Record<string, string> = {
        provider: this.provider,
        model: payload.model
      };
      if (payload.baseUrl && payload.baseUrl.trim()) {
        body.base_url = payload.baseUrl.trim();
      }
      if (payload.apiKey && payload.apiKey.trim()) {
        body.api_key = payload.apiKey.trim();
      }

      if (Object.keys(body).length <= 2) {
        return;
      }

      try {
        const response = await request<{
          provider: string;
          model: string;
          base_url: string | null;
          temperature: number;
          max_tokens: number;
          is_configured: boolean;
        }>('/settings/llm', {
          method: 'PUT',
          body
        });
        this.provider = response.provider;
        this.model = response.model;
        this.baseUrl = response.base_url || '';
        this.isConfigured = response.is_configured;
      } catch (e) {
        console.error('Failed to update server settings', e);
      }
    },
    
    updateSettings(partial: Partial<AppSettings>) {
      this.$patch(partial);
      this.persistSettings();
    },
    
    persistSettings() {
      if (!import.meta.client) return;
      window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(this.$state));
    },
    
    resetSettings() {
      this.theme = 'system';
      this.apiKey = '';
      this.baseUrl = '';
      this.defaultSlideCount = 10;
      this.model = 'gpt-4o';
      this.customModel = '';
      this.provider = 'openai';
      this.isConfigured = false;
      this.verboseMode = false;
      this.persistSettings();
    }
  }
});
