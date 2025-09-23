import React, { useState } from 'react';
import styled from 'styled-components';

const colors = {
  success: '#7ED321',      // Bright Green - for ALL message bubbles
  white: '#FFFFFF',        // White - for text inside bubbles
  textSecondary: '#666666', // Medium Gray - for timestamps
  primary: '#1976D2',      // Royal Blue - for links/actions
  lightGray: '#F5F5F5'     // Light Gray - for table alternating rows
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

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 14px;
  background-color: ${colors.white};
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const TableHeader = styled.thead`
  background-color: ${colors.primary};
  color: white;
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${colors.lightGray};
  }

  &:hover {
    background-color: #f0f8ff;
  }
`;

const TableHeaderCell = styled.th`
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
`;

const TableCell = styled.td`
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;

  &:first-child {
    font-weight: 500;
  }
`;

const TableFooter = styled.div`
  margin-top: 8px;
  font-size: 12px;
  color: ${colors.textSecondary};
  font-style: italic;
  text-align: center;
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