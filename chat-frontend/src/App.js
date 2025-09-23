import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import ChatMessage from './components/ChatMessage';
import MessageInput from './components/MessageInput';
import Header from './components/Header';
import axios from 'axios';

// Color palette constants
const colors = {
  primary: '#1976D2',      // Royal Blue
  success: '#7ED321',      // Bright Green
  white: '#FFFFFF',        // White
  background: '#F5F5F5',   // Light Gray
  textPrimary: '#333333',  // Dark Gray
  textSecondary: '#666666' // Medium Gray
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
  gap: 8px;
  padding: 16px 20px;
  background-color: ${colors.success};
  color: ${colors.white};
  border-radius: 18px;
  max-width: 200px;
  margin-left: auto;
  margin-right: 0;

  &::after {
    content: '';
    width: 20px;
    height: 20px;
    border: 2px solid ${colors.white};
    border-top: 2px solid transparent;
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
  padding: 40px 20px;
  color: ${colors.textSecondary};

  h2 {
    color: ${colors.primary};
    margin-bottom: 16px;
    font-size: 24px;
    font-weight: 600;
  }

  p {
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 24px;
  }

  .suggestions {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: 600px;
    margin: 0 auto;
  }

  .suggestion {
    background-color: ${colors.white};
    padding: 12px 16px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid #e0e0e0;

    &:hover {
      border-color: ${colors.primary};
      box-shadow: 0 2px 8px rgba(25, 118, 210, 0.1);
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
    "Show me total revenue for each event",
    "Which events sold the most tickets?",
    "What's the average order value by shop?",
    "Show monthly revenue trends"
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
              <h2>Welcome to CUBE Chat</h2>
              <p>Ask me anything about your event data using natural language!</p>
              <div className="suggestions">
                <p><strong>Try these sample questions:</strong></p>
                {sampleQuestions.map((question, index) => (
                  <div
                    key={index}
                    className="suggestion"
                    onClick={() => handleSuggestionClick(question)}
                  >
                    {question}
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
              Processing your query...
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