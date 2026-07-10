import { create } from "zustand";
import type { ConversationDTO, ExecutiveUnderstandingDTO, PortfolioItemDTO } from "../api/client";

export type GymView = "workspace" | "prompts";

interface GymState {
  view: GymView;
  portfolio: PortfolioItemDTO[];
  conversations: ConversationDTO[];
  currentConversation: ConversationDTO | null;
  coverageByCategory: Record<string, number>;
  overallCoverage: number;
  understanding: ExecutiveUnderstandingDTO | null;
  setView: (view: GymView) => void;
  setPortfolio: (items: PortfolioItemDTO[]) => void;
  setConversations: (items: ConversationDTO[]) => void;
  setCurrentConversation: (conversation: ConversationDTO | null) => void;
  appendMessages: (userMessage: ConversationDTO["messages"][number], assistantMessage: ConversationDTO["messages"][number]) => void;
  setCoverage: (coverageByCategory: Record<string, number>, overallCoverage: number) => void;
  setUnderstanding: (understanding: ExecutiveUnderstandingDTO | null) => void;
}

export const useGymStore = create<GymState>((set) => ({
  view: "workspace",
  portfolio: [],
  conversations: [],
  currentConversation: null,
  coverageByCategory: {},
  overallCoverage: 0,
  understanding: null,
  setView: (view) => set({ view }),
  setPortfolio: (items) => set({ portfolio: items }),
  setConversations: (items) => set({ conversations: items }),
  setCurrentConversation: (conversation) =>
    set({
      currentConversation: conversation,
      understanding: null,
      coverageByCategory: {},
      overallCoverage: 0,
      view: "workspace",
    }),
  appendMessages: (userMessage, assistantMessage) =>
    set((state) => {
      if (!state.currentConversation) return state;
      return {
        currentConversation: {
          ...state.currentConversation,
          messages: [...state.currentConversation.messages, userMessage, assistantMessage],
        },
      };
    }),
  setCoverage: (coverageByCategory, overallCoverage) => set({ coverageByCategory, overallCoverage }),
  setUnderstanding: (understanding) => set({ understanding }),
}));
