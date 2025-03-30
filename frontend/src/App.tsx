import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Chat from "./pages/Chat";
import Questions from "./pages/Questions";
import QuizStart from "./pages/QuizStart";
import Documents from "./pages/Documents";

import SideBar from "./components/SideBar";
function App() {
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false);
  const [chatHistory, setChatHistory] = useState<string[]>([]);

  const toggleSidebar = () => {
    setIsSidebarExpanded(!isSidebarExpanded);
  };

  const handleChatHistory = (message: string) => {
    setChatHistory([...chatHistory, message]);
  };

  return (
    <>
      <div className="flex row">
        <button onClick={() => handleChatHistory("Hello")}>Click me</button>
        <div className="flex h-screen w-screen bg-gray-100 overflow-auto">
          <SideBar
            isExpanded={isSidebarExpanded}
            toggleSidebar={toggleSidebar}
            chatHistory={chatHistory}
          />
          <Router>
            <Routes>
              <Route path="/" element={<Chat />} />
              <Route path="/questions" element={<Questions />} />
              <Route path="/quizStart" element={<QuizStart />} />
              <Route path="/documents" element={<Documents />} />
            </Routes>
          </Router>
        </div>
      </div>
    </>
  );
}

export default App;
