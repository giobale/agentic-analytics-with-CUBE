import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import ChatMessage from './components/ChatMessage';
import MessageInput from './components/MessageInput';
import Header from './components/Header';
import axios from 'axios';

// Color palette constants - Weezagent Analyst Theme
const colors = {
  primary: '#6366F1',      // Modern indigo
  secondary: '#8B5CF6',    // Purple accent
  success: '#10B981',      // Emerald green
  accent: '#F59E0B',       // Amber
  white: '#FFFFFF',        // Pure white
  background: '#F8FAFC',   // Soft blue-gray background
  cardBg: '#FFFFFF',       // Card background
  textPrimary: '#1F2937',  // Warm dark gray
  textSecondary: '#6B7280' // Cool medium gray
};

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: ${colors.background};
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  padding: 0 20px;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: ${colors.background};
  }

  &::-webkit-scrollbar-thumb {
    background: ${colors.textSecondary};
    border-radius: 3px;
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%);
  color: ${colors.white};
  border-radius: 20px;
  max-width: 240px;
  margin-left: auto;
  margin-right: 0;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25);
  font-weight: 500;

  &::after {
    content: '';
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid ${colors.white};
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 60px 24px;
  color: ${colors.textSecondary};

  h2 {
    color: ${colors.primary};
    margin-bottom: 12px;
    font-size: 32px;
    font-weight: 700;
    letter-spacing: -0.5px;
  }

  .subtitle {
    font-size: 18px;
    color: ${colors.textSecondary};
    margin-bottom: 8px;
    font-weight: 500;
  }

  .description {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 40px;
    color: ${colors.textSecondary};
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
  }

  .suggestions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    max-width: 700px;
    margin: 0 auto;
  }

  .suggestion {
    background: ${colors.cardBg};
    padding: 20px 24px;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid ${colors.background};
    position: relative;
    text-align: left;

    &:hover {
      border-color: ${colors.primary};
      box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
      transform: translateY(-2px);
    }

    &::before {
      content: '✨';
      position: absolute;
      top: 16px;
      right: 20px;
      font-size: 18px;
      opacity: 0.7;
    }

    .question-text {
      font-weight: 500;
      color: ${colors.textPrimary};
      margin-bottom: 8px;
    }

    .question-type {
      font-size: 13px;
      color: ${colors.textSecondary};
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 600;
    }
  }
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sampleQuestions = [
    { text: "📈 Show me total revenue for each event", type: "Revenue Analysis" },
    { text: "🎫 Which events sold the most tickets?", type: "Performance Analytics" },
    { text: "💰 What's the average order value by payment method?", type: "Payment Insights" },
    { text: "📊 Show monthly revenue trends", type: "Trend Analysis" },
    { text: "🏆 Which event categories perform best?", type: "Category Performance" },
    { text: "⏰ Show me orders placed in the last 7 days", type: "Recent Activity" }
  ];

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send request to orchestrator
      const response = await axios.post('/api/query', {
        query: text.trim()
      });

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        text: response.data.description || 'Query processed successfully',
        sender: 'assistant',
        timestamp: new Date(),
        data: response.data
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  return (
    <AppContainer>
      <Header />
      <ChatContainer>
        <MessagesContainer>
          {messages.length === 0 ? (
            <WelcomeMessage>
              <h2>🚀 Welcome to Weezagent Analyst</h2>
              <div className="subtitle">Your AI-powered event analytics companion</div>
              <div className="description">
                Get instant insights from your event data using natural language.
                Ask questions about revenue, attendance, trends, and performance metrics.
              </div>
              <div className="suggestions">
                {sampleQuestions.map((question, index) => (
                  <div
                    key={index}
                    className="suggestion"
                    onClick={() => handleSuggestionClick(question.text)}
                  >
                    <div className="question-text">{question.text}</div>
                    <div className="question-type">{question.type}</div>
                  </div>
                ))}
              </div>
            </WelcomeMessage>
          ) : (
            messages.map(message => (
              <ChatMessage key={message.id} message={message} />
            ))
          )}

          {isLoading && (
            <LoadingIndicator>
              🤖 Analyzing your event data...
            </LoadingIndicator>
          )}

          <div ref={messagesEndRef} />
        </MessagesContainer>

        <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </ChatContainer>
    </AppContainer>
  );
}

export default App;