import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Check, RefreshCw, Loader2, Plus } from 'lucide-react';
import CodeMirror from '@uiw/react-codemirror';
import { markdown } from '@codemirror/lang-markdown';
import {
  getOutline,
  updateOutline,
  confirmOutline,
  addSupplement,
  ApiError,
} from '../api/client';

export default function OutlinePage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [outline, setOutline] = useState('');
  const [originalOutline, setOriginalOutline] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [supplementText, setSupplementText] = useState('');
  const [showSupplement, setShowSupplement] = useState(false);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    if (sessionId) {
      loadOutline();
    }
  }, [sessionId]);

  const loadOutline = async () => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await getOutline(sessionId);
      setOutline(response.outline);
      setOriginalOutline(response.outline);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('加载大纲失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!sessionId || outline === originalOutline) return;

    setSaving(true);
    setError(null);

    try {
      await updateOutline(sessionId, outline);
      setOriginalOutline(outline);
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

  const handleConfirm = async () => {
    if (!sessionId) return;

    // Save first if there are changes
    if (outline !== originalOutline) {
      await handleSave();
    }

    setConfirming(true);
    setError(null);

    try {
      await confirmOutline(sessionId);
      navigate(`/generating/${sessionId}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('确认失败');
      }
      setConfirming(false);
    }
  };

  const handleAddSupplement = async () => {
    if (!sessionId || !supplementText.trim()) return;

    setRegenerating(true);
    setError(null);

    try {
      const response = await addSupplement(sessionId, supplementText.trim());
      setOutline(response.outline);
      setOriginalOutline(response.outline);
      setSupplementText('');
      setShowSupplement(false);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('重新生成失败');
      }
    } finally {
      setRegenerating(false);
    }
  };

  const hasChanges = outline !== originalOutline;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">编辑大纲</h1>
            <p className="text-sm text-gray-500">
              审核并编辑生成的演示大纲，确认后开始生成幻灯片
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowSupplement(!showSupplement)}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Plus className="h-4 w-4" />
            补充需求
          </button>
          {hasChanges && (
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
            >
              {saving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              保存
            </button>
          )}
          <button
            onClick={handleConfirm}
            disabled={confirming}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {confirming ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Check className="h-4 w-4" />
            )}
            确认并生成
          </button>
        </div>
      </div>

      {/* Supplement Input */}
      {showSupplement && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-medium text-blue-800 mb-2">
            补充需求
          </h3>
          <textarea
            rows={3}
            className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="添加更多需求细节，AI将重新生成大纲..."
            value={supplementText}
            onChange={(e) => setSupplementText(e.target.value)}
            disabled={regenerating}
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={() => setShowSupplement(false)}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800"
            >
              取消
            </button>
            <button
              onClick={handleAddSupplement}
              disabled={!supplementText.trim() || regenerating}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {regenerating ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <RefreshCw className="h-3.5 w-3.5" />
              )}
              重新生成
            </button>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Editor */}
      <div className="border border-gray-300 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-4 py-2 border-b border-gray-300">
          <span className="text-sm font-medium text-gray-700">
            Markdown 大纲
          </span>
          {hasChanges && (
            <span className="ml-2 text-xs text-orange-600">（未保存）</span>
          )}
        </div>
        <CodeMirror
          value={outline}
          height="500px"
          extensions={[markdown()]}
          onChange={(value) => setOutline(value)}
          theme="light"
          basicSetup={{
            lineNumbers: true,
            highlightActiveLineGutter: true,
            highlightActiveLine: true,
            foldGutter: true,
          }}
        />
      </div>

      {/* Tips */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-2">编辑提示</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• 使用 # 设置演示主题，## 设置章节标题</li>
          <li>• 使用 - 或 * 添加要点列表</li>
          <li>• 每个章节将转换为一张幻灯片</li>
          <li>• 确认后将开始生成最终的Slidev演示文稿</li>
        </ul>
      </div>
    </div>
  );
}