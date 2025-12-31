import { defineStore } from 'pinia';

export type SessionStatus =
  | 'idle'
  | 'pending'
  | 'outline_ready'
  | 'draft'
  | 'confirmed'
  | 'generating'
  | 'assembling'
  | 'completed'
  | 'error';

export type WorkflowStage =
  | 'initial'
  | 'outline_generated'
  | 'outline_confirmed'
  | 'vue_generating'
  | 'vue_completed'
  | 'pagination_review'
  | 'slidev_assembling'
  | 'completed'
  | 'error';

export interface Message {
  id: string;
  role: 'user' | 'agent' | 'meta';
  content: string;
  timestamp: number;
}

export interface ComponentArtifact {
  name: string;
  code: string;
  [key: string]: unknown;
}

export interface GenerationResult {
  session_id: string;
  slides_md: string;
  components: ComponentArtifact[];
  slides: Array<Record<string, unknown>>;
}

export interface SessionHistoryEntry {
  id: string;
  title: string;
  createdAt: number;
  status: SessionStatus;
}

const HISTORY_KEY = 'html2ppt_agent_history';

const createId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export const useSessionStore = defineStore('session', {
  state: () => ({
    sessionId: '' as string,
    status: 'idle' as SessionStatus,
    stage: 'initial' as WorkflowStage,
    progress: 0,
    outline: '',
    messages: [] as Message[],
    result: null as GenerationResult | null,
    error: '' as string,
    isPolling: false,
    history: [] as SessionHistoryEntry[],
    pollTimer: null as ReturnType<typeof setInterval> | null
  }),
  getters: {
    isGenerating: (state) =>
      ['pending', 'confirmed', 'generating', 'assembling'].includes(state.status),
    hasSession: (state) => Boolean(state.sessionId)
  },
  actions: {
    ensureIntro() {
      if (this.messages.length === 0) {
        this.messages.push({
          id: createId(),
          role: 'agent',
          content: 'Describe the deck you want. I will draft an outline and build the Slidev preview.',
          timestamp: Date.now()
        });
      }
    },
    initHistory() {
      if (!import.meta.client) return;
      const raw = window.localStorage.getItem(HISTORY_KEY);
      if (!raw) return;
      try {
        this.history = JSON.parse(raw) as SessionHistoryEntry[];
      } catch {
        this.history = [];
      }
    },
    persistHistory() {
      if (!import.meta.client) return;
      window.localStorage.setItem(HISTORY_KEY, JSON.stringify(this.history));
    },
    rememberSession(title: string) {
      const entry: SessionHistoryEntry = {
        id: this.sessionId,
        title: title.slice(0, 64),
        createdAt: Date.now(),
        status: this.status
      };
      this.history = [entry, ...this.history.filter((item) => item.id !== entry.id)].slice(0, 8);
      this.persistHistory();
    },
    updateHistoryStatus() {
      if (!this.sessionId) return;
      const match = this.history.find((item) => item.id === this.sessionId);
      if (match) {
        match.status = this.status;
        this.persistHistory();
      }
    },
    resetSession() {
      this.sessionId = '';
      this.status = 'idle';
      this.stage = 'initial';
      this.progress = 0;
      this.outline = '';
      this.result = null;
      this.error = '';
      this.messages = [];
      this.stopPolling();
      this.ensureIntro();
    },
    addMessage(role: Message['role'], content: string) {
      this.messages.push({
        id: createId(),
        role,
        content,
        timestamp: Date.now()
      });
    },
    async sendPrompt(prompt: string) {
      const trimmed = prompt.trim();
      if (!trimmed) return;
      this.ensureIntro();
      this.addMessage('user', trimmed);

      if (!this.sessionId || this.status === 'completed' || this.status === 'error') {
        await this.startSession(trimmed);
        return;
      }

      if (['draft', 'outline_ready'].includes(this.status)) {
        await this.addSupplement(trimmed);
        return;
      }

      this.addMessage(
        'meta',
        'Generation is running. I will apply new requests after the current run finishes.'
      );
    },
    async startSession(prompt: string) {
      const { request } = useApi();
      this.status = 'pending';
      this.error = '';
      this.result = null;
      this.addMessage('agent', 'Drafting the outline and structuring the deck flow.');

      try {
        const response = await request<{
          session_id: string;
          outline: string;
          status: SessionStatus;
        }>('/requirements', {
          method: 'POST',
          body: { content: prompt }
        });

        this.sessionId = response.session_id;
        this.outline = response.outline || '';
        this.status = response.status || 'draft';
        this.stage = response.status === 'draft' ? 'outline_generated' : 'initial';
        this.addMessage('agent', 'Outline ready. Review and confirm to continue.');
        this.rememberSession(prompt);
      } catch (error: unknown) {
        this.status = 'error';
        this.error = error instanceof Error ? error.message : 'Failed to start session.';
        this.addMessage('agent', `Error: ${this.error}`);
      }
    },
    async addSupplement(supplement: string) {
      if (!this.sessionId) return;
      const { request } = useApi();
      this.addMessage('agent', 'Updating the outline with your follow-up.');

      try {
        const response = await request<{
          session_id: string;
          outline: string;
          status: SessionStatus;
        }>(`/outline/${this.sessionId}/supplement`, {
          method: 'POST',
          body: { content: supplement }
        });
        this.outline = response.outline || this.outline;
        this.status = response.status || 'draft';
        this.stage = 'outline_generated';
        this.addMessage('agent', 'Outline updated. Confirm when you are ready.');
      } catch (error: unknown) {
        this.error = error instanceof Error ? error.message : 'Failed to add supplement.';
        this.status = 'error';
        this.addMessage('agent', `Error: ${this.error}`);
      }
    },
    async updateOutline(outline: string) {
      if (!this.sessionId) return;
      const { request } = useApi();

      try {
        const response = await request<{
          session_id: string;
          outline: string;
          status: SessionStatus;
        }>(`/outline/${this.sessionId}`, {
          method: 'PUT',
          body: { outline }
        });
        this.outline = response.outline;
        this.status = response.status || 'draft';
        this.addMessage('agent', 'Outline saved. Confirm to start generation.');
      } catch (error: unknown) {
        this.error = error instanceof Error ? error.message : 'Failed to update outline.';
        this.status = 'error';
        this.addMessage('agent', `Error: ${this.error}`);
      }
    },
    async confirmOutline() {
      if (!this.sessionId) return;
      const { request } = useApi();

      this.addMessage('agent', 'Generating slides and components now.');
      try {
        const response = await request<{
          session_id: string;
          status: SessionStatus;
          stage: WorkflowStage;
          progress: number;
          error?: string;
        }>(`/outline/${this.sessionId}/confirm`, {
          method: 'POST'
        });

        this.status = response.status || 'generating';
        this.stage = response.stage || 'outline_confirmed';
        this.progress = response.progress || 0;
        this.startPolling();
      } catch (error: unknown) {
        this.error = error instanceof Error ? error.message : 'Failed to confirm outline.';
        this.status = 'error';
        this.addMessage('agent', `Error: ${this.error}`);
      }
    },
    async fetchStatus() {
      if (!this.sessionId) return;
      const { request } = useApi();

      try {
        const status = await request<{
          session_id: string;
          status: SessionStatus;
          stage: WorkflowStage;
          progress: number;
          error?: string;
        }>(`/generation/${this.sessionId}/status`);

        this.status = status.status || 'pending';
        this.stage = status.stage || 'initial';
        this.progress = status.progress || 0;
        this.error = status.error || '';
        this.updateHistoryStatus();

        if (this.status === 'completed') {
          this.stopPolling();
          await this.fetchResult();
        }

        if (this.status === 'error') {
          this.stopPolling();
        }
      } catch (error: unknown) {
        this.error = error instanceof Error ? error.message : 'Failed to fetch status.';
        this.status = 'error';
        this.stopPolling();
      }
    },
    startPolling() {
      if (this.isPolling) return;
      this.isPolling = true;
      this.pollTimer = setInterval(() => {
        void this.fetchStatus();
      }, 2000);
    },
    stopPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer);
      }
      this.pollTimer = null;
      this.isPolling = false;
    },
    async fetchResult() {
      if (!this.sessionId) return;
      const { request } = useApi();

      try {
        const result = await request<GenerationResult>(`/result/${this.sessionId}`);
        this.result = result;
        this.status = 'completed';
        this.stage = 'completed';
        this.progress = 1;
      } catch (error: unknown) {
        this.error = error instanceof Error ? error.message : 'Failed to fetch result.';
        this.status = 'error';
      }
    },
    async loadSession(sessionId: string) {
      if (!sessionId) return;
      const { request } = useApi();
      this.sessionId = sessionId;
      this.result = null;
      this.error = '';
      this.messages = [];
      this.ensureIntro();
      this.addMessage('meta', `Loaded session ${sessionId.slice(0, 8)}.`);

      try {
        const outline = await request<{
          session_id: string;
          outline: string;
          status: SessionStatus;
        }>(`/outline/${sessionId}`);
        this.outline = outline.outline || '';
        this.status = outline.status || 'draft';
        await this.fetchStatus();
        if (this.status === 'completed') {
          await this.fetchResult();
        } else {
          this.startPolling();
        }
      } catch (error: unknown) {
        this.error = error instanceof Error ? error.message : 'Failed to load session.';
        this.status = 'error';
      }
    }
  }
});
