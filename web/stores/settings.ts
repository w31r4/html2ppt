import { defineStore } from 'pinia';

export type ThemeOption = 'light' | 'dark' | 'system';

export interface AppSettings {
  theme: ThemeOption;
  apiKey: string;
  defaultSlideCount: number;
  model: string;
  verboseMode: boolean;
}

const SETTINGS_KEY = 'html2ppt_agent_settings';

export const useSettingsStore = defineStore('settings', {
  state: (): AppSettings => ({
    theme: 'system',
    apiKey: '',
    defaultSlideCount: 10,
    model: 'gpt-4o',
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
      this.defaultSlideCount = 10;
      this.model = 'gpt-4o';
      this.verboseMode = false;
      this.persistSettings();
    }
  }
});
