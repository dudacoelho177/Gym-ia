import { useEffect } from "react";
import "./styles/theme.css";
import { Shell } from "./components/Shell";
import { Sidebar } from "./components/Sidebar";
import { ServiceForm } from "./components/ServiceForm";
import { ChatView } from "./components/ChatView";
import { PromptsPage } from "./components/PromptsPage";
import { api } from "./api/client";
import { useGymStore } from "./store/useGymStore";

function App() {
  const setPortfolio = useGymStore((s) => s.setPortfolio);
  const setConversations = useGymStore((s) => s.setConversations);
  const currentConversation = useGymStore((s) => s.currentConversation);
  const setCurrentConversation = useGymStore((s) => s.setCurrentConversation);
  const view = useGymStore((s) => s.view);

  useEffect(() => {
    api.listPortfolio().then(setPortfolio).catch(console.error);
    api.listConversations().then(setConversations).catch(console.error);
  }, [setPortfolio, setConversations]);

  function renderMain() {
    if (view === "prompts") return <PromptsPage />;
    return currentConversation ? <ChatView /> : <ServiceForm />;
  }

  return (
    <Shell sidebar={<Sidebar onNewChat={() => setCurrentConversation(null)} />} main={renderMain()} />
  );
}

export default App;
