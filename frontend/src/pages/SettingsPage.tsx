import { useState, useEffect } from 'react';
import { Save, Loader2, CheckCircle } from 'lucide-react';
import { getLLMSettings, updateLLMSettings, ApiError, LLMSettings } from '../api/client';

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'gemini', label: 'Google Gemini' },
  { value: 'azure_openai', label: 'Azure OpenAI' },
];

const PRESET_MODELS: Record<string, string[]> = {
  openai: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  gemini: ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash'],
  azure_openai: ['gpt-4', 'gpt-4-turbo', 'gpt-35-turbo'],
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<LLMSettings>({
    provider: 'openai',
    model: 'gpt-4o',
    temperature: 0.7,
    max_tokens: 4096,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await getLLMSettings();
      setSettings(data);
    } catch (err) {
      // Use defaults if settings not available
      console.warn('Could not load settings, using defaults');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);

    try {
      await updateLLMSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('保存失败');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleProviderChange = (provider: string) => {
    const models = PRESET_MODELS[provider] || [];
    setSettings({
      ...settings,
      provider,
      model: models[0] || '',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">设置</h1>
        <p className="text-gray-600 mt-1">配置LLM后端和生成参数</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6">
        {/* Provider */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            LLM 提供商
          </label>
          <select
            value={settings.provider}
            onChange={(e) => handleProviderChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            {PROVIDERS.map((provider) => (
              <option key={provider.value} value={provider.value}>
                {provider.label}
              </option>
            ))}
          </select>
        </div>

        {/* Model */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            模型
          </label>
          <select
            value={settings.model}
            onChange={(e) => setSettings({ ...settings, model: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            {(PRESET_MODELS[settings.provider] || []).map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
          <p className="mt-1 text-sm text-gray-500">
            选择要使用的模型，推荐使用 GPT-4o 或 Gemini 2.0
          </p>
        </div>

        {/* Base URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            自定义API端点 (可选)
          </label>
          <input
            type="text"
            value={settings.base_url || ''}
            onChange={(e) => setSettings({ ...settings, base_url: e.target.value || undefined })}
            placeholder="例如: http://localhost:11434/v1 (Ollama)"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            留空使用官方API，或填写自定义端点如vLLM、Ollama、OpenRouter等
          </p>
        </div>

        {/* Temperature */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Temperature: {settings.temperature}
          </label>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={settings.temperature}
            onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>精确 (0)</span>
            <span>平衡 (0.7)</span>
            <span>创意 (2)</span>
          </div>
        </div>

        {/* Max Tokens */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            最大Token数
          </label>
          <input
            type="number"
            min="256"
            max="32000"
            value={settings.max_tokens}
            onChange={(e) => setSettings({ ...settings, max_tokens: parseInt(e.target.value) || 4096 })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Save Button */}
        <div className="flex items-center gap-4 pt-4">
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : saved ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {saved ? '已保存' : '保存设置'}
          </button>

          {saved && (
            <span className="text-sm text-green-600">设置已保存</span>
          )}
        </div>
      </div>

      {/* Info */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-sm font-medium text-blue-800 mb-2">提示</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• API密钥需要在服务器端的 .env 文件中配置</li>
          <li>• 推荐使用 Gemini 2.0 Flash 获得最佳性价比</li>
          <li>• OpenAI兼容端点支持vLLM、Ollama等本地部署方案</li>
        </ul>
      </div>
    </div>
  );
}