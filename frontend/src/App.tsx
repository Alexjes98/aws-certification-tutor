import { useState, type ChangeEvent, type FormEvent } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Chat from "./pages/Chat";

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
        <SideBar
          isExpanded={isSidebarExpanded}
          toggleSidebar={toggleSidebar}
          chatHistory={chatHistory}
        />
        <Router>
          <Routes>
            <Route path="/" element={<Chat />} />
          </Routes>
        </Router>
      </div>
    </>
  );
}

export default App;
