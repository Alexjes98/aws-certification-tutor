import type React from "react";
import {
  ChevronLeft,
  ChevronRight,
  Home,
  Book,
  History,
  FileQuestion,
} from "lucide-react";
interface SidebarProps {
  isExpanded: boolean;
  toggleSidebar: () => void;
  chatHistory: string[];
}

const SideBar: React.FC<SidebarProps> = ({
  isExpanded,
  toggleSidebar,
  chatHistory,
}) => {
  return (
    <div
      className={`bg-gray-800 text-white transition-all duration-300 ${
        isExpanded ? "w-64" : "w-16"
      }`}
    >
      <div className="flex justify-end p-4">
        <button
          onClick={toggleSidebar}
          className="text-gray-400 hover:text-white"
        >
          {isExpanded ? <ChevronLeft size={24} /> : <ChevronRight size={24} />}
        </button>
      </div>
      <nav className="mt-8">
        <ul>
          <li className="mb-4">
            <a
              href="/"
              className="flex items-center px-4 py-2 hover:bg-gray-700"
            >
              <Home size={24} />
              {isExpanded && <span className="ml-4">Home</span>}
            </a>
          </li>
          <li className="mb-4">
            <a
              href="/questions"
              className="flex items-center px-4 py-2 hover:bg-gray-700"
            >
              <Book size={24} />
              {isExpanded && <span className="ml-4">Courses</span>}
            </a>
          </li>
          <li className="mb-4">
            <a
              href="/quizStart"
              className="flex items-center px-4 py-2 hover:bg-gray-700"
            >
              <FileQuestion size={24} />
              {isExpanded && <span className="ml-4">Start Quiz</span>}
            </a>
          </li>
        </ul>
      </nav>
      {isExpanded && (
        <div className="mt-8 px-4">
          <h3 className="text-lg font-semibold mb-2">Recent Chats</h3>
          <ul>
            {chatHistory.slice(-5).map((message, index) => (
              <li key={index} className="mb-2 truncate">
                {message}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SideBar;
