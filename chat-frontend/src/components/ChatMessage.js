import React, { useState } from 'react';
import styled from 'styled-components';

const colors = {
  success: '#7ED321',      // Bright Green - for ALL message bubbles
  white: '#FFFFFF',        // White - for text inside bubbles
  textSecondary: '#666666', // Medium Gray - for timestamps
  primary: '#1976D2'       // Royal Blue - for links/actions
};

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 16px;
`;

const MessageBubble = styled.div`
  background-color: ${colors.success};
  color: ${colors.white};
  padding: 12px 16px;
  border-radius: 18px;
  max-width: 70%;
  word-wrap: break-word;
  line-height: 1.4;
  font-size: 14px;

  ${props => props.isUser ? `
    border-bottom-right-radius: 4px;
  ` : `
    border-bottom-left-radius: 4px;
  `}

  ${props => props.isError && `
    background-color: #FF6B6B;
  `}
`;

const MessageInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: ${colors.textSecondary};
`;

const Timestamp = styled.span`
  font-size: 12px;
  color: ${colors.textSecondary};
`;

const ResultsContainer = styled.div`
  margin-top: 12px;
  background-color: ${colors.white};
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 100%;
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
`;

const ResultsTitle = styled.h4`
  margin: 0;
  color: ${colors.primary};
  font-size: 14px;
  font-weight: 600;
`;

const DownloadButton = styled.button`
  background-color: ${colors.primary};
  color: ${colors.white};
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 0.8;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const DataPreview = styled.div`
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: ${colors.textSecondary};
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: ${colors.primary};
  font-size: 12px;
  cursor: pointer;
  margin-top: 8px;
  text-decoration: underline;

  &:hover {
    opacity: 0.8;
  }
`;

const ChatMessage = ({ message }) => {
  const [showData, setShowData] = useState(false);

  const formatTimestamp = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleDownloadCSV = () => {
    if (message.data && message.data.csv_filename) {
      // Create download link for CSV
      const csvUrl = `/api/download/${message.data.csv_filename}`;
      const link = document.createElement('a');
      link.href = csvUrl;
      link.download = message.data.csv_filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const renderDataPreview = () => {
    if (!message.data || !message.data.cube_data) return null;

    const data = message.data.cube_data;
    const preview = Array.isArray(data) ? data.slice(0, 5) : [data];

    return (
      <DataPreview>
        {JSON.stringify(preview, null, 2)}
        {Array.isArray(data) && data.length > 5 && (
          <div style={{ marginTop: '8px', fontStyle: 'italic' }}>
            ... and {data.length - 5} more rows
          </div>
        )}
      </DataPreview>
    );
  };

  return (
    <MessageContainer isUser={message.sender === 'user'}>
      <MessageBubble isUser={message.sender === 'user'} isError={message.isError}>
        {message.text}
      </MessageBubble>

      <MessageInfo>
        <Timestamp>{formatTimestamp(message.timestamp)}</Timestamp>
        {message.sender === 'user' && <span>You</span>}
        {message.sender === 'assistant' && <span>CUBE Assistant</span>}
      </MessageInfo>

      {/* Show results for successful assistant responses */}
      {message.sender === 'assistant' && message.data && !message.isError && (
        <ResultsContainer>
          <ResultsHeader>
            <ResultsTitle>
              Query Results
              {message.data.row_count && ` (${message.data.row_count} rows)`}
            </ResultsTitle>
            {message.data.csv_filename && (
              <DownloadButton onClick={handleDownloadCSV}>
                Download CSV
              </DownloadButton>
            )}
          </ResultsHeader>

          {message.data.cube_data && (
            <>
              <ToggleButton onClick={() => setShowData(!showData)}>
                {showData ? 'Hide' : 'Show'} Data Preview
              </ToggleButton>
              {showData && renderDataPreview()}
            </>
          )}
        </ResultsContainer>
      )}
    </MessageContainer>
  );
};

export default ChatMessage;