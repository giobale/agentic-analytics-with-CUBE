import React, { useState } from 'react';
import styled from 'styled-components';

const colors = {
  primary: '#6366F1',      // Modern indigo
  secondary: '#8B5CF6',    // Purple accent
  success: '#10B981',      // Emerald green
  accent: '#F59E0B',       // Amber
  white: '#FFFFFF',        // Pure white
  background: '#F8FAFC',   // Soft blue-gray background
  cardBg: '#FFFFFF',       // Card background
  textPrimary: '#1F2937',  // Warm dark gray
  textSecondary: '#6B7280', // Cool medium gray
  lightGray: '#F1F5F9'     // Light blue-gray for table rows
};

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 16px;
`;

const MessageBubble = styled.div`
  background: ${props => props.isUser
    ? `linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%)`
    : colors.cardBg
  };
  color: ${props => props.isUser ? colors.white : colors.textPrimary};
  padding: 16px 20px;
  border-radius: 20px;
  max-width: 75%;
  word-wrap: break-word;
  line-height: 1.5;
  font-size: 15px;
  font-weight: 400;
  box-shadow: ${props => props.isUser
    ? '0 4px 20px rgba(99, 102, 241, 0.25)'
    : '0 2px 12px rgba(0, 0, 0, 0.08)'
  };
  border: ${props => props.isUser ? 'none' : `1px solid ${colors.background}`};

  ${props => props.isUser ? `
    border-bottom-right-radius: 6px;
  ` : `
    border-bottom-left-radius: 6px;
  `}

  ${props => props.isError && `
    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
    color: ${colors.white};
  `}
`;

const MessageInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 12px;
  color: ${colors.textSecondary};
  font-weight: 500;
`;

const Timestamp = styled.span`
  font-size: 12px;
  color: ${colors.textSecondary};
`;

const ResultsContainer = styled.div`
  margin-top: 16px;
  background-color: ${colors.cardBg};
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  max-width: 100%;
  border: 1px solid ${colors.background};
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid ${colors.background};
`;

const ResultsTitle = styled.h4`
  margin: 0;
  color: ${colors.primary};
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;

  &::before {
    content: '📊';
    font-size: 18px;
  }
`;

const DownloadButton = styled.button`
  background: linear-gradient(135deg, ${colors.success} 0%, ${colors.accent} 100%);
  color: ${colors.white};
  border: none;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;

  &::before {
    content: '💾';
    font-size: 14px;
  }

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;


const ToggleButton = styled.button`
  background: ${colors.background};
  border: 2px solid ${colors.primary};
  color: ${colors.primary};
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 12px;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;

  &::before {
    content: '👁️';
    font-size: 14px;
  }

  &:hover {
    background: ${colors.primary};
    color: ${colors.white};
    transform: translateY(-1px);
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
  font-size: 14px;
  background-color: ${colors.cardBg};
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid ${colors.background};
`;

const TableHeader = styled.thead`
  background: linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%);
  color: white;
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${colors.lightGray};
  }

  &:hover {
    background-color: rgba(99, 102, 241, 0.05);
  }
`;

const TableHeaderCell = styled.th`
  padding: 16px 20px;
  text-align: left;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
`;

const TableCell = styled.td`
  padding: 14px 20px;
  border-bottom: 1px solid ${colors.background};
  vertical-align: top;
  font-size: 14px;
  color: ${colors.textPrimary};

  &:first-child {
    font-weight: 600;
    color: ${colors.primary};
  }
`;

const TableFooter = styled.div`
  margin-top: 12px;
  font-size: 13px;
  color: ${colors.textSecondary};
  font-weight: 500;
  text-align: center;
  padding: 8px 16px;
  background: ${colors.background};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;

  &::before {
    content: 'ℹ️';
    font-size: 14px;
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

  const renderDataTable = () => {
    if (!message.data || !message.data.data) return null;

    const data = message.data.data;
    if (!Array.isArray(data) || data.length === 0) return null;

    // Show maximum 10 rows
    const preview = data.slice(0, 10);
    const hasMoreRows = data.length > 10;

    // Get column headers from the first row
    const headers = Object.keys(preview[0]);

    // Helper function to format column names (remove prefixes and make readable)
    const formatColumnName = (columnName) => {
      return columnName
        .replace(/^[^.]*\./, '') // Remove prefix like "EventPerformanceOverview."
        .replace(/_/g, ' ') // Replace underscores with spaces
        .replace(/\b\w/g, l => l.toUpperCase()); // Capitalize first letter of each word
    };

    // Helper function to format cell values
    const formatCellValue = (value) => {
      if (value === null || value === undefined) return '-';
      if (typeof value === 'number') {
        // Format large numbers with commas
        return new Intl.NumberFormat().format(value);
      }
      return String(value);
    };

    return (
      <>
        <Table>
          <TableHeader>
            <TableRow>
              {headers.map((header) => (
                <TableHeaderCell key={header}>
                  {formatColumnName(header)}
                </TableHeaderCell>
              ))}
            </TableRow>
          </TableHeader>
          <tbody>
            {preview.map((row, index) => (
              <TableRow key={index}>
                {headers.map((header) => (
                  <TableCell key={header}>
                    {formatCellValue(row[header])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </tbody>
        </Table>
        {hasMoreRows && (
          <TableFooter>
            Showing first 10 of {data.length} rows. Download CSV for complete data.
          </TableFooter>
        )}
      </>
    );
  };

  return (
    <MessageContainer isUser={message.sender === 'user'}>
      <MessageBubble isUser={message.sender === 'user'} isError={message.isError}>
        {message.text}
      </MessageBubble>

      <MessageInfo>
        <Timestamp>{formatTimestamp(message.timestamp)}</Timestamp>
        {message.sender === 'user' && <span>👤 You</span>}
        {message.sender === 'assistant' && <span>🤖 Weezagent Analyst</span>}
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

          {message.data.data && (
            <>
              <ToggleButton onClick={() => setShowData(!showData)}>
                {showData ? 'Hide' : 'Show'} Data Table
              </ToggleButton>
              {showData && renderDataTable()}
            </>
          )}
        </ResultsContainer>
      )}
    </MessageContainer>
  );
};

export default ChatMessage;