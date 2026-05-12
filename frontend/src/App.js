import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { FiDownload, FiMoon, FiSun } from "react-icons/fi";

// 🔥 USER ID
const getUserId = () => {
  let id = localStorage.getItem("user_id");
  if (!id) {
    id = "user_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("user_id", id);
  }
  return id;
};

const userId = getUserId();

function App() {
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [input, setInput] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);

  const [downloadMenu, setDownloadMenu] = useState({
    visible: false,
    content: "",
    question: "",
  });

  const chatEndRef = useRef(null);

  // 🔥 LOAD HISTORY
  useEffect(() => {
    const fetchHistory = async () => {
      const res = await fetch(`http://127.0.0.1:8000/history/${userId}`);
      const data = await res.json();
      setHistory(data.reverse());
    };

    fetchHistory();
  }, []);

  // 🔥 SEND MESSAGE
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);

    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, question: input }),
      });

      const data = await res.json();

      const botMsg = {
        role: "bot",
        content: data.answer,
        sources: data.sources,
      };

      setMessages((prev) => [...prev, botMsg]);

      setHistory((prev) => [
        {
          question: input,
          answer: data.answer,
          sources: data.sources,
        },
        ...prev,
      ]);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  // 🔥 LOAD CHAT
  const loadChat = (chat) => {
    setMessages([
      { role: "user", content: chat.question },
      {
        role: "bot",
        content: chat.answer,
        sources: chat.sources,
      },
    ]);
  };

  // 🔥 DOWNLOAD FUNCTION
  const downloadFile = async (type, content, question) => {
    const endpoint =
      type === "csv"
        ? "http://127.0.0.1:8000/export-csv"
        : "http://127.0.0.1:8000/export-pdf";

    const res = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content, question }),
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const name = (question || "response")
      .replace(/[^a-zA-Z0-9 ]/g, "")
      .replace(/\s+/g, "_")
      .slice(0, 30);

    const a = document.createElement("a");
    a.href = url;
    a.download = `${name}.${type}`;
    a.click();

    setDownloadMenu({ visible: false, content: "", question: "" });
  };

  // 🔥 FULL CHAT DOWNLOAD
  const downloadFullChat = () => {
    let text = "";
    messages.forEach((m) => {
      text += `${m.role}: ${m.content}\n\n`;
    });

    setDownloadMenu({
      visible: true,
      content: text,
      question: "chat",
    });
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="h-screen flex bg-gray-100 dark:bg-gray-900">

        {/* SIDEBAR */}
        <div className="w-1/4 bg-gray-200 dark:bg-gray-800 p-4 overflow-y-auto">
          <h2 className="font-bold mb-3 dark:text-white">💬 History</h2>

          <button
            onClick={() => setMessages([])}
            className="w-full mb-4 bg-blue-500 text-white py-2 rounded"
          >
            + New Chat
          </button>

          {history.map((chat, i) => (
            <div
              key={i}
              onClick={() => loadChat(chat)}
              className="p-2 mb-2 bg-white dark:bg-gray-700 rounded cursor-pointer text-sm dark:text-white"
            >
              {chat.question.slice(0, 40)}...
            </div>
          ))}
        </div>

        {/* CHAT */}
        <div className="flex-1 flex flex-col">

          {/* HEADER */}
          <div className="flex justify-between items-center px-6 py-4 bg-white dark:bg-gray-800 shadow">
            <h2 className="text-lg font-semibold dark:text-white">
              🌍 Geoscience Chatbot
            </h2>

            <div className="flex gap-4">
              <button onClick={() => setDarkMode(!darkMode)}>
                {darkMode ? <FiSun /> : <FiMoon />}
              </button>

              <button onClick={downloadFullChat}>
                <FiDownload />
              </button>
            </div>
          </div>

          {/* MESSAGES */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">

            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-2xl p-4 rounded-2xl shadow relative ${
                    msg.role === "user"
                      ? "bg-green-500 text-white"
                      : "bg-white dark:bg-gray-700 dark:text-white"
                  }`}
                >
                  {/* DOWNLOAD BUTTON */}
                  {msg.role === "bot" && (
                    <button
                      onClick={() =>
                        setDownloadMenu({
                          visible: true,
                          content: msg.content,
                          question: messages[index - 1]?.content,
                        })
                      }
                      className="absolute top-2 right-2 text-gray-400"
                    >
                      <FiDownload size={16} />
                    </button>
                  )}

                  {/* ANSWER */}
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>

                  {/* SOURCES */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 text-xs text-blue-500">
                      <strong>Sources:</strong>
                      {msg.sources.map((s, i) => (
                        <div key={i}>
                          <a href={s} target="_blank" rel="noopener noreferrer">
                            {s}
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && <div>⏳ Bot is typing...</div>}

            <div ref={chatEndRef} />
          </div>

          {/* INPUT */}
          <div className="p-4 bg-white dark:bg-gray-800 border-t flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask something..."
              className="flex-1 p-3 border rounded-lg dark:bg-gray-700 dark:text-white"
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />

            <button
              onClick={sendMessage}
              className="bg-blue-500 text-white px-5 py-2 rounded-lg"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* DOWNLOAD POPUP */}
      {downloadMenu.visible && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg text-center">
            <h3 className="mb-4 font-semibold dark:text-white">
              Download as:
            </h3>

            <div className="flex gap-4 justify-center">
              <button
                onClick={() =>
                  downloadFile("pdf", downloadMenu.content, downloadMenu.question)
                }
                className="bg-blue-500 text-white px-4 py-2 rounded"
              >
                PDF
              </button>

              <button
                onClick={() =>
                  downloadFile("csv", downloadMenu.content, downloadMenu.question)
                }
                className="bg-green-500 text-white px-4 py-2 rounded"
              >
                CSV
              </button>
            </div>

            <button
              onClick={() =>
                setDownloadMenu({ visible: false, content: "", question: "" })
              }
              className="mt-4 text-sm text-gray-500"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;