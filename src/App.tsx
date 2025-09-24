import { useState, useRef, useEffect } from 'react'
import './App.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages([...messages, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage: Message = { role: 'assistant', content: data.response }
        setMessages([...messages, userMessage, assistantMessage])
      } else {
        const errorMessage: Message = { role: 'assistant', content: 'Error: Unable to get response' }
        setMessages([...messages, userMessage, errorMessage])
      }
    } catch (error) {
      const errorMessage: Message = { role: 'assistant', content: 'Error: Network error' }
      setMessages([...messages, userMessage, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const formatMessage = (content: string) => {
    return content.split('\n').map((line, index) => (
      <span key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </span>
    ))
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>FinanceX HuggingGPT</h1>
          <div className="model-indicator">
            <div className="status-dot"></div>
            <span>Online</span>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="chat-container">
          <div className="messages-container">
            {messages.length === 0 && (
              <div className="welcome-message">
                <h2>How can I help you today?</h2>
                <p>Ask me about investments, savings, loans, or any financial questions you have.</p>
              </div>
            )}

            <div className="messages">
              {messages.map((message, index) => (
                <div key={index} className={`message-wrapper ${message.role}`}>
                  <div className={`message ${message.role}`}>
                    <div className="message-content">
                      {formatMessage(message.content)}
                    </div>
                    <div className="message-time">
                      {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message-wrapper assistant">
                  <div className="message assistant">
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="input-container">
            <form onSubmit={handleSubmit} className="input-form">
              <div className="input-wrapper">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(e)
                    }
                  }}
                  placeholder="Ask about investments, savings, loans..."
                  disabled={isLoading}
                  rows={1}
                  className="message-input"
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="send-button"
                >
                  {isLoading ? (
                    <div className="spinner"></div>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                    </svg>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
