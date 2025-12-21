import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Copy, Check, Eye, Code, FileText, Loader2 } from 'lucide-react';
import { getResult, getExportUrl, ApiError, GenerationResult } from '../api/client';
import VuePreview from '../components/VuePreview';

type TabType = 'preview' | 'markdown' | 'components';

export default function ResultPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [result, setResult] = useState<GenerationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('preview');
  const [copied, setCopied] = useState(false);
  const [selectedComponent, setSelectedComponent] = useState(0);

  useEffect(() => {
    if (sessionId) {
      loadResult();
    }
  }, [sessionId]);

  const loadResult = async () => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getResult(sessionId);
      setResult(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('加载结果失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result?.slides_md) return;

    try {
      await navigator.clipboard.writeText(result.slides_md);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = result.slides_md;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = (includeComponents = false) => {
    if (!sessionId) return;
    window.open(getExportUrl(sessionId, includeComponents), '_blank');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
          <p className="text-red-600">{error}</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="text-primary-600 hover:text-primary-800 underline"
        >
          返回首页
        </button>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  const componentMap = new Map(
    result.components.map((component) => [component.name, component.code])
  );

  return (
    <div className="max-w-6xl mx-auto">
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
            <h1 className="text-2xl font-bold text-gray-900">生成结果</h1>
            <p className="text-sm text-gray-500">
              您的Slidev演示文稿已准备就绪
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4 text-green-500" />
                已复制
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                复制
              </>
            )}
          </button>
          <button
            onClick={() => handleDownload(false)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Download className="h-4 w-4" />
            下载 slides.md
          </button>
          <button
            onClick={() => handleDownload(true)}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="h-4 w-4" />
            下载组件包
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-6">
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex items-center gap-2 py-3 border-b-2 transition-colors ${
              activeTab === 'preview'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Eye className="h-4 w-4" />
            预览
          </button>
          <button
            onClick={() => setActiveTab('markdown')}
            className={`flex items-center gap-2 py-3 border-b-2 transition-colors ${
              activeTab === 'markdown'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <FileText className="h-4 w-4" />
            Markdown
          </button>
          <button
            onClick={() => setActiveTab('components')}
            className={`flex items-center gap-2 py-3 border-b-2 transition-colors ${
              activeTab === 'components'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Code className="h-4 w-4" />
            Vue组件
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {activeTab === 'preview' && (
          <div className="p-6">
            <div className="space-y-6">
              {result.slides.map((slide, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg overflow-hidden"
                >
                  <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-600">
                      Slide {index + 1}
                    </span>
                  </div>
                  <div className="p-6 bg-white aspect-video flex items-center justify-center">
                    {slide.component_name && componentMap.has(slide.component_name) ? (
                      <VuePreview
                        code={componentMap.get(slide.component_name) || ''}
                        className="h-full w-full"
                      />
                    ) : (
                      <div
                        className="prose max-w-none"
                        dangerouslySetInnerHTML={{
                          __html: slide.content
                            .replace(/^#\s+(.+)$/gm, '<h1>$1</h1>')
                            .replace(/^##\s+(.+)$/gm, '<h2>$1</h2>')
                            .replace(/^-\s+(.+)$/gm, '<li>$1</li>')
                            .replace(/(<li>.*<\/li>)+/g, '<ul>$&</ul>'),
                        }}
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'markdown' && (
          <div className="relative">
            <pre className="p-6 overflow-auto max-h-[600px] text-sm font-mono bg-gray-900 text-gray-100">
              <code>{result.slides_md}</code>
            </pre>
          </div>
        )}

        {activeTab === 'components' && (
          <div className="flex">
            {/* Component List */}
            <div className="w-64 border-r border-gray-200 bg-gray-50">
              <div className="p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                  组件列表
                </h3>
                <div className="space-y-1">
                  {result.components.map((component, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedComponent(index)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                        selectedComponent === index
                          ? 'bg-primary-100 text-primary-700'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {component.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Component Code */}
            <div className="flex-1">
              {result.components[selectedComponent] && (
                <div>
                  <div className="bg-gray-100 px-4 py-2 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-700">
                      {result.components[selectedComponent].name}.vue
                    </span>
                  </div>
                  <pre className="p-4 overflow-auto max-h-[500px] text-sm font-mono bg-gray-900 text-gray-100">
                    <code>{result.components[selectedComponent].code}</code>
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Usage Instructions */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">使用说明</h3>
        <ol className="space-y-3 text-gray-600">
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              1
            </span>
            <span>下载 slides.md 文件</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              2
            </span>
            <span>
              创建Slidev项目：<code className="bg-gray-200 px-1.5 py-0.5 rounded text-sm">npm init slidev@latest</code>
            </span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              3
            </span>
            <span>将 slides.md 内容替换到项目的 slides.md 文件中</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              4
            </span>
            <span>将生成的 .vue 组件放到项目的 components/ 目录中</span>
          </li>
          <li className="flex gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
              5
            </span>
            <span>
              运行开发服务器：<code className="bg-gray-200 px-1.5 py-0.5 rounded text-sm">npm run dev</code>
            </span>
          </li>
        </ol>
      </div>
    </div>
  );
}
