<template>
  <div class="max-w-3xl mx-auto animate-fade-in">
    <header class="mb-8">
      <h1 class="text-3xl font-semibold text-text-light dark:text-text-dark mb-2">Settings</h1>
      <p class="text-gray-500 dark:text-gray-400">Manage your preferences and application configuration.</p>
    </header>

    <div class="flex flex-col gap-6">
      <!-- Appearance Section -->
      <section class="card">
        <div class="p-5 border-b border-border-light dark:border-border-dark">
          <h3 class="text-lg font-semibold text-text-light dark:text-text-dark">Appearance</h3>
        </div>
        <div class="p-5">
          <div class="mb-5">
            <label class="block font-medium text-sm text-text-light dark:text-text-dark mb-2">Theme</label>
            <div class="flex gap-3">
              <label
                v-for="option in themeOptions"
                :key="option.value"
                class="flex-1 border rounded-lg p-3 text-center cursor-pointer transition-all"
                :class="settings.theme === option.value
                  ? 'border-primary bg-primary/5 text-primary font-medium'
                  : 'border-border-light dark:border-border-dark bg-white dark:bg-card-dark text-text-light dark:text-text-dark hover:bg-gray-50 dark:hover:bg-gray-800'"
              >
                <input
                  type="radio"
                  :value="option.value"
                  v-model="settings.theme"
                  class="sr-only"
                  :aria-label="option.label"
                />
                <span class="material-symbols-rounded text-xl mb-1 block">{{ option.icon }}</span>
                <span class="text-sm">{{ option.label }}</span>
              </label>
            </div>
          </div>
        </div>
      </section>

      <!-- Generation Defaults Section -->
      <section class="card">
        <div class="p-5 border-b border-border-light dark:border-border-dark">
          <h3 class="text-lg font-semibold text-text-light dark:text-text-dark">Generation Defaults</h3>
        </div>
        <div class="p-5 space-y-5">
          <div>
            <label for="slideCount" class="block font-medium text-sm text-text-light dark:text-text-dark mb-2">
              Default Slide Count
            </label>
            <input
              id="slideCount"
              type="number"
              v-model.number="settings.defaultSlideCount"
              min="1"
              max="50"
              class="w-full px-3 py-2.5 border border-border-light dark:border-border-dark rounded-lg bg-white dark:bg-card-dark text-text-light dark:text-text-dark focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
            />
            <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 block">
              Target number of slides for new decks.
            </span>
          </div>

          <div>
            <label for="modelPreset" class="block font-medium text-sm text-text-light dark:text-text-dark mb-2">
              Model Preset
            </label>
            <select
              id="modelPreset"
              v-model="settings.model"
              class="w-full px-3 py-2.5 border border-border-light dark:border-border-dark rounded-lg bg-white dark:bg-card-dark text-text-light dark:text-text-dark focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
            >
              <option v-for="option in modelOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 block">
              Choose a preset or override with a custom model name.
            </span>
          </div>

          <div>
            <label for="customModel" class="block font-medium text-sm text-text-light dark:text-text-dark mb-2">
              Custom Model
            </label>
            <input
              id="customModel"
              v-model="settings.customModel"
              type="text"
              placeholder="e.g. gpt-4o-mini, claude-3-5-sonnet"
              class="w-full px-3 py-2.5 border border-border-light dark:border-border-dark rounded-lg bg-white dark:bg-card-dark text-text-light dark:text-text-dark placeholder:text-gray-400 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
            />
            <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 block">
              When filled, this value will be used instead of the preset.
            </span>
          </div>
        </div>
      </section>

      <!-- API Configuration Section -->
      <section class="card">
        <div class="p-5 border-b border-border-light dark:border-border-dark">
          <h3 class="text-lg font-semibold text-text-light dark:text-text-dark">API Configuration</h3>
        </div>
        <div class="p-5 space-y-5">
          <div>
            <label for="baseUrl" class="block font-medium text-sm text-text-light dark:text-text-dark mb-2">
              Base URL
            </label>
            <input
              id="baseUrl"
              v-model="settings.baseUrl"
              type="text"
              placeholder="https://api.openai.com/v1"
              class="w-full px-3 py-2.5 border border-border-light dark:border-border-dark rounded-lg bg-white dark:bg-card-dark text-text-light dark:text-text-dark placeholder:text-gray-400 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
            />
            <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 block">
              Leave empty to use the server .env default. Common for OpenAI-compatible gateways.
            </span>
          </div>

          <div>
            <label for="apiKey" class="block font-medium text-sm text-text-light dark:text-text-dark mb-2">
              API Key
            </label>
            <input
              id="apiKey"
              type="password"
              v-model="settings.apiKey"
              placeholder="sk-..."
              class="w-full px-3 py-2.5 border border-border-light dark:border-border-dark rounded-lg bg-white dark:bg-card-dark text-text-light dark:text-text-dark placeholder:text-gray-400 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
            />
            <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 block">
              Leave empty to use server environment variables.
              <span v-if="settingsStore.isConfigured" class="text-green-600 dark:text-green-400 font-medium">
                Server key detected.
              </span>
            </span>
          </div>
        </div>
      </section>

      <!-- Actions -->
      <div class="flex gap-4">
        <button
          class="btn btn-primary"
          @click="saveSettings"
          :disabled="saving"
        >
          <span class="material-symbols-rounded text-lg" v-if="!saving">save</span>
          <span class="material-symbols-rounded text-lg animate-spin" v-else>progress_activity</span>
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
        <button class="btn btn-ghost" @click="resetDefaults">
          <span class="material-symbols-rounded text-lg">restart_alt</span>
          Reset to Defaults
        </button>
      </div>

      <!-- Save Feedback -->
      <div
        v-if="saveMessage"
        class="flex items-center gap-2 px-4 py-3 rounded-lg"
        :class="saveSuccess ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400'"
      >
        <span class="material-symbols-rounded">{{ saveSuccess ? 'check_circle' : 'error' }}</span>
        {{ saveMessage }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';

import { useSettingsStore } from '@/stores/settings';

const settingsStore = useSettingsStore();
const settings = ref({ ...settingsStore.$state });
const saving = ref(false);
const saveMessage = ref('');
const saveSuccess = ref(false);

const themeOptions = [
  { value: 'light', label: 'Light', icon: 'light_mode' },
  { value: 'dark', label: 'Dark', icon: 'dark_mode' },
  { value: 'system', label: 'System', icon: 'contrast' }
];

const modelOptions = [
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'claude-3-5-sonnet', label: 'Claude 3.5 Sonnet' }
];

onMounted(() => {
  settingsStore.initSettings();
  settingsStore.fetchServerSettings().then(() => {
    settings.value = { ...settingsStore.$state };
    syncModelSelection();
  });
});

// Watch for theme changes and apply immediately
watch(() => settings.value.theme, (newTheme) => {
  applyTheme(newTheme);
});

const applyTheme = (theme: string) => {
  const root = document.documentElement;
  if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
};

const syncModelSelection = () => {
  const match = modelOptions.find((option) => option.value === settings.value.model);
  if (match) {
    settings.value.customModel = '';
    return;
  }
  settings.value.customModel = settings.value.model;
  settings.value.model = modelOptions[0].value;
};

const saveSettings = async () => {
  saving.value = true;
  saveMessage.value = '';

  try {
    settingsStore.updateSettings(settings.value);
    const modelValue = settings.value.customModel.trim() || settings.value.model;
    await settingsStore.saveLlmSettings({
      model: modelValue,
      baseUrl: settings.value.baseUrl,
      apiKey: settings.value.apiKey
    });
    saveSuccess.value = true;
    saveMessage.value = 'Settings saved successfully!';
  } catch (error) {
    saveSuccess.value = false;
    saveMessage.value = 'Failed to save settings. Please try again.';
  } finally {
    saving.value = false;
    setTimeout(() => {
      saveMessage.value = '';
    }, 3000);
  }
};

const resetDefaults = () => {
  settingsStore.resetSettings();
  settings.value = { ...settingsStore.$state };
  settingsStore.fetchServerSettings().then(() => {
    settings.value = { ...settingsStore.$state };
    syncModelSelection();
  });
};
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
