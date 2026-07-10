const BASE_URL = import.meta.env.VITE_API_BASE_URL as string;
const API_KEY = import.meta.env.VITE_API_KEY as string;

export interface MessageDTO {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface ConversationDTO {
  id: string;
  service_type: string;
  briefing: string;
  title: string;
  created_at: string;
  messages: MessageDTO[];
}

export interface SendMessageResponse {
  assistant_message: MessageDTO;
  coverage_by_category: Record<string, number>;
  overall_coverage: number;
}

export interface PortfolioItemDTO {
  id: string;
  category: string;
  name: string;
  description: string;
  aliases: string[];
  is_active: boolean;
}

export interface ExecutiveUnderstandingDTO {
  id: string;
  summary: string;
  diagnosis: string;
  missing_information: string[];
  risks: string[];
  assumptions: string[];
  next_steps: string[];
  complexity: string;
  human_review_notice: string;
  version: number;
}

export interface ArtifactDTO {
  id: string;
  kind: string;
  title: string;
  content: string;
}

export interface PromptVersionDTO {
  id: string;
  version_number: number;
  content: string;
  created_at: string;
}

export interface PromptDTO {
  id: string;
  name: string;
  is_active: boolean;
  active_version_id: string | null;
  versions: PromptVersionDTO[];
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...options.headers,
    },
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API ${response.status}: ${body}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export interface DiscoveryStateDTO {
  coverage_by_category: Record<string, number>;
  overall_coverage: number;
}

export const api = {
  listPortfolio: () => request<PortfolioItemDTO[]>("/portfolio/items"),
  listConversations: () => request<ConversationDTO[]>("/conversations"),
  getConversation: (id: string) => request<ConversationDTO>(`/conversations/${id}`),
  getDiscoveryState: (id: string) => request<DiscoveryStateDTO>(`/conversations/${id}/state`),
  createConversation: (payload: { service_type: string; briefing: string; title: string }) =>
    request<ConversationDTO>("/conversations", { method: "POST", body: JSON.stringify(payload) }),
  sendMessage: (conversationId: string, content: string) =>
    request<SendMessageResponse>(`/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  generateUnderstanding: (conversationId: string) =>
    request<ExecutiveUnderstandingDTO>(`/conversations/${conversationId}/understanding`, { method: "POST" }),
  generateArtifacts: (conversationId: string, kinds: string[]) =>
    request<ArtifactDTO[]>(`/conversations/${conversationId}/artifacts`, {
      method: "POST",
      body: JSON.stringify({ kinds }),
    }),
  getActivePrompt: () => request<PromptDTO | null>("/prompts/active"),
  savePrompt: (payload: { name: string; content: string }) =>
    request<PromptDTO>("/prompts/active", { method: "PUT", body: JSON.stringify(payload) }),
  activatePromptVersion: (versionId: string) =>
    request<PromptDTO>(`/prompts/active/versions/${versionId}/activate`, { method: "POST" }),
};
