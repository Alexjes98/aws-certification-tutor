
import type React from "react"
import { useState, type ChangeEvent, type FormEvent } from "react"
import { Send, Upload } from "lucide-react"

interface ChatDashboardProps {
  addMessageToHistory: (message: string) => void
}

const ChatDashboard: React.FC<ChatDashboardProps> = ({ addMessageToHistory }) => {
  const [message, setMessage] = useState("")
  const [file, setFile] = useState<File | null>(null)

  const handleMessageChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      addMessageToHistory(message)
      setMessage("")
    }
    if (file) {
      addMessageToHistory(`File uploaded: ${file.name}`)
      setFile(null)
    }
  }

  return (
    <div className="flex-grow flex flex-col p-6">
      <div className="flex-grow bg-white rounded-lg shadow-md p-6 mb-6 overflow-y-auto">
        {/* Chat messages would be displayed here */}
      </div>
      <form onSubmit={handleSubmit} className="flex items-center space-x-4">
        <textarea
          value={message}
          onChange={handleMessageChange}
          className="flex-grow p-2 border rounded-md resize-none"
          placeholder="Type your message here..."
          rows={3}
        />
        <div className="flex flex-col space-y-2">
          <label htmlFor="file-upload" className="cursor-pointer bg-gray-200 hover:bg-gray-300 p-2 rounded-md">
            <Upload size={24} />
            <input id="file-upload" type="file" onChange={handleFileChange} className="hidden" />
          </label>
          <button type="submit" className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-md">
            <Send size={24} />
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatDashboard

