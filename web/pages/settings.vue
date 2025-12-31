<template>
  <div class="settings-page">
    <header class="page-header">
      <h1>Settings</h1>
      <p>Manage your preferences and application configuration.</p>
    </header>

    <div class="settings-grid">
      <section class="card">
        <div class="card-header">
          <h3>Appearance</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>Theme</label>
            <div class="radio-group">
              <label class="radio-card" :class="{ active: settings.theme === 'light' }">
                <input type="radio" value="light" v-model="settings.theme" />
                <span>Light</span>
              </label>
              <label class="radio-card" :class="{ active: settings.theme === 'dark' }">
                <input type="radio" value="dark" v-model="settings.theme" />
                <span>Dark</span>
              </label>
              <label class="radio-card" :class="{ active: settings.theme === 'system' }">
                <input type="radio" value="system" v-model="settings.theme" />
                <span>System</span>
              </label>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-header">
          <h3>Generation Defaults</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>Default Slide Count</label>
            <input 
              type="number" 
              v-model.number="settings.defaultSlideCount" 
              min="1" 
              max="50"
              class="input-field"
            />
            <span class="hint">Target number of slides for new decks.</span>
          </div>

          <div class="form-group">
            <label>Model</label>
            <select v-model="settings.model" class="input-field">
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
            </select>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-header">
          <h3>API Configuration</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>API Key</label>
            <input 
              type="password" 
              v-model="settings.apiKey" 
              placeholder="sk-..."
              class="input-field"
            />
            <span class="hint">Your OpenAI or Anthropic API key. Leave empty to use server environment variables.</span>
          </div>
        </div>
      </section>
      
      <div class="actions">
        <button class="btn-primary" @click="saveSettings">Save Changes</button>
        <button class="btn-ghost" @click="resetDefaults">Reset to Defaults</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const settingsStore = useSettingsStore();
const settings = ref({ ...settingsStore.$state });

onMounted(() => {
  settingsStore.initSettings();
  settings.value = { ...settingsStore.$state };
});

const saveSettings = () => {
  settingsStore.updateSettings(settings.value);
  // Show toast or feedback here
};

const resetDefaults = () => {
  settingsStore.resetSettings();
  settings.value = { ...settingsStore.$state };
};
</script>

<style scoped>
.settings-page {
  max-width: 800px;
  margin: 0 auto;
  animation: rise 0.6s ease both;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-family: var(--font-serif);
  font-size: 2rem;
  margin: 0 0 8px;
}

.page-header p {
  color: var(--muted);
  margin: 0;
}

.settings-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  font-weight: 500;
  font-size: 0.9rem;
}

.input-field {
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  width: 100%;
  background: #fff;
}

.hint {
  font-size: 0.8rem;
  color: var(--muted);
}

.radio-group {
  display: flex;
  gap: 12px;
}

.radio-card {
  flex: 1;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fff;
}

.radio-card:hover {
  background: var(--surface-warm);
}

.radio-card.active {
  border-color: var(--accent-teal);
  background: rgba(47, 167, 160, 0.05);
  color: var(--accent-teal);
  font-weight: 500;
}

.radio-card input {
  display: none;
}

.actions {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.btn-primary {
  background: var(--accent-teal);
  color: #fff;
  border: none;
  padding: 10px 24px;
  border-radius: var(--radius-sm);
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--line);
  padding: 10px 24px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.2s;
}

.btn-ghost:hover {
  background: var(--surface-warm);
}
</style>