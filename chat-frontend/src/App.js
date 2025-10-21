import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import ChatMessage from './components/ChatMessage';
import MessageInput from './components/MessageInput';
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import SavedQueries from './components/SavedQueries';
import MetricsCatalog from './components/MetricsCatalog';
import axios from 'axios';
import { colors, shadows, borderRadius, spacing } from './theme/weezeventTheme';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: ${colors.white};
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1360px;
  margin: 0 auto;
  width: 100%;
  padding: 0 ${spacing.xl};
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${spacing.xl} 0;
  display: flex;
  flex-direction: column;
  gap: ${spacing.lg};

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: ${colors.gray100};
    border-radius: ${borderRadius.full};
  }

  &::-webkit-scrollbar-thumb {
    background: ${colors.gray400};
    border-radius: ${borderRadius.full};

    &:hover {
      background: ${colors.gray500};
    }
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.md};
  padding: ${spacing.lg} ${spacing.xl};
  background: ${colors.primary};
  color: ${colors.white};
  border-radius: ${borderRadius.xl};
  max-width: 280px;
  margin-left: auto;
  margin-right: 0;
  box-shadow: ${shadows.primary};
  font-weight: 600;
  font-size: 15px;

  &::after {
    content: '';
    width: 18px;
    height: 18px;
    border: 3px solid rgba(255, 255, 255, 0.2);
    border-top: 3px solid ${colors.white};
    border-radius: ${borderRadius.full};
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: ${spacing['4xl']} ${spacing.xl};
  color: ${colors.textSecondary};

  h2 {
    color: ${colors.black};
    margin-bottom: ${spacing.md};
    font-size: 40px;
    font-weight: 700;
    letter-spacing: -1px;
  }

  .subtitle {
    font-size: 20px;
    color: ${colors.textSecondary};
    margin-bottom: ${spacing.lg};
    font-weight: 400;
  }

  .description {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: ${spacing['3xl']};
    color: ${colors.gray600};
    max-width: 560px;
    margin-left: auto;
    margin-right: auto;
  }

  .suggestions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: ${spacing.lg};
    max-width: 800px;
    margin: 0 auto;
  }

  .suggestion {
    background: ${colors.white};
    padding: ${spacing.xl};
    border-radius: ${borderRadius.lg};
    cursor: pointer;
    transition: all 0.2s ease;
    border: 2px solid ${colors.gray200};
    position: relative;
    text-align: left;
    box-shadow: ${shadows.sm};

    &:hover {
      border-color: ${colors.primary};
      box-shadow: ${shadows.primary};
      transform: translateY(-2px);
    }

    &::before {
      content: '→';
      position: absolute;
      top: ${spacing.xl};
      right: ${spacing.xl};
      font-size: 24px;
      font-weight: bold;
      color: ${colors.primary};
      opacity: 0;
      transition: opacity 0.2s ease;
    }

    &:hover::before {
      opacity: 1;
    }

    .question-text {
      font-weight: 600;
      color: ${colors.black};
      margin-bottom: ${spacing.sm};
      font-size: 15px;
      line-height: 1.4;
    }

    .question-type {
      font-size: 12px;
      color: ${colors.gray500};
      text-transform: uppercase;
      letter-spacing: 0.8px;
      font-weight: 600;
    }
  }
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [savedQueries, setSavedQueries] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sampleQuestions = [
    { text: "Show me total revenue for each event", type: "Revenue Analysis" },
    { text: "Which events sold the most tickets?", type: "Performance Analytics" },
    { text: "What's the average order value by payment method?", type: "Payment Insights" },
    { text: "Show monthly revenue trends", type: "Trend Analysis" },
    { text: "Which event categories perform best?", type: "Category Performance" },
    { text: "Show me orders placed in the last 7 days", type: "Recent Activity" }
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

      console.log('API Response:', response.data);

      // Handle different response types
      const responseType = response.data.response_type;
      let assistantMessage;

      if (responseType === 'clarification') {
        // Handle clarification needed
        assistantMessage = {
          id: Date.now() + 1,
          text: response.data.description || 'I need more information to process your query',
          sender: 'assistant',
          timestamp: new Date(),
          responseType: 'clarification',
          data: response.data
        };
      } else if (responseType === 'data_result') {
        // Handle successful data result
        assistantMessage = {
          id: Date.now() + 1,
          text: response.data.description || 'Query processed successfully',
          sender: 'assistant',
          timestamp: new Date(),
          responseType: 'data_result',
          data: response.data
        };
      } else {
        // Handle other successful responses
        assistantMessage = {
          id: Date.now() + 1,
          text: response.data.description || 'Query processed successfully',
          sender: 'assistant',
          timestamp: new Date(),
          responseType: responseType,
          data: response.data
        };
      }

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      console.error('Error response:', error.response?.data);

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: error.response?.data?.detail || 'Sorry, I encountered an error processing your request. Please try again.',
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

  const handleSaveQuery = (query) => {
    // Add query to saved queries if not already saved
    const existingQuery = savedQueries.find(q => q.id === query.id);
    if (!existingQuery) {
      setSavedQueries(prev => [query, ...prev]);
      console.log('Query saved:', query);
    }
  };

  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
  };

  return (
    <AppContainer>
      <Header />
      <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />

      {activeTab === 'chat' && (
        <ChatContainer>
          <MessagesContainer>
            {messages.length === 0 ? (
              <WelcomeMessage>
                <h2>Welcome to Weezagent Analyst</h2>
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
                <ChatMessage
                  key={message.id}
                  message={message}
                  onSuggestionClick={handleSendMessage}
                  onSaveQuery={handleSaveQuery}
                />
              ))
            )}

            {isLoading && (
              <LoadingIndicator>
                Analyzing your event data...
              </LoadingIndicator>
            )}

            <div ref={messagesEndRef} />
          </MessagesContainer>

          <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </ChatContainer>
      )}

      {activeTab === 'saved-queries' && (
        <SavedQueries savedQueries={savedQueries} />
      )}

      {activeTab === 'metrics-catalog' && (
        <MetricsCatalog />
      )}
    </AppContainer>
  );
}

export default App;