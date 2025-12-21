import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { submitRequirements, ApiError } from '../api/client';

export default function HomePage() {
  const navigate = useNavigate();
  const [requirement, setRequirement] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!requirement.trim()) {
      setError('请输入需求描述');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await submitRequirements(requirement.trim());
      navigate(`/outline/${response.session_id}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('提交失败，请重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-primary-100 rounded-full">
            <Sparkles className="h-12 w-12 text-primary-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI演示文稿生成器
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          描述您的演示需求，AI将为您生成专业的Slidev演示文稿。
          支持大纲编辑、实时预览和一键导出。
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="requirement"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            需求描述
          </label>
          <textarea
            id="requirement"
            rows={8}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
            placeholder="例如：为我的产品发布会制作一个演示文稿，包括产品介绍、核心功能、竞争优势和定价方案..."
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            disabled={loading}
            maxLength={10000}
          />
          <div className="flex justify-between mt-2 text-sm text-gray-500">
            <span>详细描述您的演示文稿需求</span>
            <span>{requirement.length} / 10000</span>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !requirement.trim()}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              正在生成大纲...
            </>
          ) : (
            <>
              <Send className="h-5 w-5" />
              生成演示大纲
            </>
          )}
        </button>
      </form>

      {/* Features */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
            <span className="text-2xl">📝</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">智能大纲</h3>
          <p className="text-gray-600 text-sm">
            AI自动分析需求，生成结构化的演示大纲
          </p>
        </div>
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
            <span className="text-2xl">✏️</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">自由编辑</h3>
          <p className="text-gray-600 text-sm">
            支持Markdown编辑，随时调整演示内容
          </p>
        </div>
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
            <span className="text-2xl">🎨</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Slidev导出</h3>
          <p className="text-gray-600 text-sm">
            一键导出Slidev格式，支持自定义主题
          </p>
        </div>
      </div>
    </div>
  );
}