import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import { getGenerationStatus, ApiError } from '../api/client';

interface StageInfo {
  key: string;
  label: string;
  description: string;
}

const STAGES: StageInfo[] = [
  {
    key: 'outline_confirmed',
    label: '大纲确认',
    description: '大纲已确认，准备生成',
  },
  {
    key: 'vue_generating',
    label: '生成Vue组件',
    description: '正在为每个章节生成Vue组件...',
  },
  {
    key: 'vue_completed',
    label: 'Vue组件完成',
    description: '所有组件已生成',
  },
  {
    key: 'slidev_assembling',
    label: '组装Slidev',
    description: '正在生成Slidev Markdown...',
  },
  {
    key: 'completed',
    label: '生成完成',
    description: '演示文稿已准备就绪',
  },
];

export default function GeneratingPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [currentStage, setCurrentStage] = useState('');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!sessionId || !polling) return;

    const pollStatus = async () => {
      try {
        const status = await getGenerationStatus(sessionId);
        setCurrentStage(status.stage);
        setProgress(status.progress);

        if (status.stage === 'completed') {
          setPolling(false);
          // Navigate to result page after a short delay
          setTimeout(() => {
            navigate(`/result/${sessionId}`);
          }, 1500);
        } else if (status.stage === 'error') {
          setPolling(false);
          setError(status.error || '生成过程中出现错误');
        }
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('获取状态失败');
        }
        setPolling(false);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [sessionId, polling, navigate]);

  const getCurrentStageIndex = () => {
    return STAGES.findIndex((s) => s.key === currentStage);
  };

  const getStageStatus = (index: number) => {
    const currentIndex = getCurrentStageIndex();
    if (currentIndex < 0) return 'pending';
    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'current';
    return 'pending';
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          正在生成演示文稿
        </h1>
        <p className="text-gray-600">
          AI正在为您创建精美的Slidev演示文稿，请稍候...
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mb-12">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>进度</span>
          <span>{Math.round(progress * 100)}%</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-600 rounded-full transition-all duration-500"
            style={{ width: `${progress * 100}%` }}
          />
        </div>
      </div>

      {/* Stages */}
      <div className="space-y-4">
        {STAGES.map((stage, index) => {
          const status = getStageStatus(index);
          return (
            <div
              key={stage.key}
              className={`flex items-start gap-4 p-4 rounded-lg border ${
                status === 'current'
                  ? 'bg-primary-50 border-primary-200'
                  : status === 'completed'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {status === 'completed' ? (
                  <CheckCircle className="h-6 w-6 text-green-500" />
                ) : status === 'current' ? (
                  <Loader2 className="h-6 w-6 text-primary-600 animate-spin" />
                ) : (
                  <Clock className="h-6 w-6 text-gray-400" />
                )}
              </div>
              <div className="flex-1">
                <h3
                  className={`font-medium ${
                    status === 'current'
                      ? 'text-primary-900'
                      : status === 'completed'
                      ? 'text-green-900'
                      : 'text-gray-500'
                  }`}
                >
                  {stage.label}
                </h3>
                <p
                  className={`text-sm ${
                    status === 'current'
                      ? 'text-primary-700'
                      : status === 'completed'
                      ? 'text-green-700'
                      : 'text-gray-400'
                  }`}
                >
                  {stage.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Error */}
      {error && (
        <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-3">
            <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div>
              <h3 className="font-medium text-red-900">生成失败</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              <button
                onClick={() => navigate('/')}
                className="mt-3 text-sm text-red-600 hover:text-red-800 underline"
              >
                返回首页重试
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="mt-12 text-center text-sm text-gray-500">
        <p>生成过程可能需要1-2分钟，请耐心等待</p>
      </div>
    </div>
  );
}
