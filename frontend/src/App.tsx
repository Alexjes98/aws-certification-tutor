import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Chat from "./pages/Chat";
import Questions from "./pages/Questions";
import QuizStart from "./pages/QuizStart";

import SideBar from "./components/SideBar";
function App() {
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false);
  const [chatHistory, setChatHistory] = useState<string[]>([]);

  const toggleSidebar = () => {
    setIsSidebarExpanded(!isSidebarExpanded);
  };

  return (
    <>
      <div className="flex row">
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
            </Routes>
          </Router>
        </div>
      </div>
    </>
  );
}

export default App;
