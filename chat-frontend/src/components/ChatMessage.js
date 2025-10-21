import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { colors, shadows, borderRadius, spacing } from '../theme/weezeventTheme';

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: ${spacing.lg};
`;

const MessageBubble = styled.div`
  background: ${props => props.isUser
    ? colors.primary
    : colors.white
  };
  color: ${props => props.isUser ? colors.white : colors.black};
  padding: ${spacing.lg} ${spacing.xl};
  border-radius: ${borderRadius.lg};
  max-width: 75%;
  word-wrap: break-word;
  line-height: 1.5;
  font-size: 15px;
  font-weight: 400;
  box-shadow: ${props => props.isUser
    ? shadows.primary
    : shadows.md
  };
  border: ${props => props.isUser ? 'none' : `1px solid ${colors.gray200}`};

  ${props => props.isUser ? `
    border-bottom-right-radius: ${borderRadius.sm};
  ` : `
    border-bottom-left-radius: ${borderRadius.sm};
  `}

  ${props => props.isError && `
    background: ${colors.error};
    color: ${colors.white};
    border: none;
  `}
`;

const MessageInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  margin-top: ${spacing.sm};
  font-size: 12px;
  color: ${colors.gray500};
  font-weight: 500;
`;

const Timestamp = styled.span`
  font-size: 12px;
  color: ${colors.gray500};
`;

const ResultsContainer = styled.div`
  margin-top: ${spacing.lg};
  background-color: ${colors.white};
  border-radius: ${borderRadius.lg};
  padding: ${spacing.xl};
  box-shadow: ${shadows.md};
  max-width: 100%;
  border: 1px solid ${colors.gray200};
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${spacing.lg};
  padding-bottom: ${spacing.md};
  border-bottom: 2px solid ${colors.gray200};
`;

const ResultsTitle = styled.h4`
  margin: 0;
  color: ${colors.black};
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
`;

const DownloadButton = styled.button`
  background: ${colors.success};
  color: ${colors.white};
  border: none;
  padding: ${spacing.sm} ${spacing.lg};
  border-radius: ${borderRadius.md};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};

  &:hover:not(:disabled) {
    background: ${colors.success};
    transform: translateY(-1px);
    box-shadow: ${shadows.md};
    filter: brightness(1.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const GenerateReportButton = styled.button`
  background: ${colors.primary};
  color: ${colors.white};
  border: none;
  padding: ${spacing.sm} ${spacing.lg};
  border-radius: ${borderRadius.md};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  margin-left: ${spacing.sm};

  &:hover:not(:disabled) {
    background: ${colors.primaryDark};
    transform: translateY(-1px);
    box-shadow: ${shadows.primary};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const SaveQueryButton = styled.button`
  background: ${colors.white};
  color: ${colors.primary};
  border: 2px solid ${colors.primary};
  padding: ${spacing.sm} ${spacing.lg};
  border-radius: ${borderRadius.md};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  margin-left: ${spacing.sm};

  &:hover:not(:disabled) {
    background: ${colors.primary};
    color: ${colors.white};
    transform: translateY(-1px);
    box-shadow: ${shadows.primary};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  &.saved {
    background: ${colors.success};
    color: ${colors.white};
    border-color: ${colors.success};

    &:hover {
      background: ${colors.success};
      filter: brightness(1.1);
    }
  }
`;

const ToggleButton = styled.button`
  background: ${colors.white};
  border: 2px solid ${colors.primary};
  color: ${colors.primary};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-top: ${spacing.md};
  padding: ${spacing.sm} ${spacing.lg};
  border-radius: ${borderRadius.md};
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};

  &:hover {
    background: ${colors.primary};
    color: ${colors.white};
    transform: translateY(-1px);
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: ${spacing.lg};
  font-size: 14px;
  background-color: ${colors.white};
  border-radius: ${borderRadius.md};
  overflow: hidden;
  box-shadow: ${shadows.sm};
  border: 1px solid ${colors.gray200};
`;

const TableHeader = styled.thead`
  background: ${colors.primary};
  color: ${colors.white};
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${colors.gray50};
  }

  &:hover {
    background-color: rgba(0, 51, 255, 0.03);
  }
`;

const TableHeaderCell = styled.th`
  padding: ${spacing.lg} ${spacing.xl};
  text-align: left;
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border-bottom: 2px solid ${colors.primaryDark};
`;

const TableCell = styled.td`
  padding: ${spacing.md} ${spacing.xl};
  border-bottom: 1px solid ${colors.gray200};
  vertical-align: top;
  font-size: 14px;
  color: ${colors.black};

  &:first-child {
    font-weight: 600;
    color: ${colors.primary};
  }
`;

const TableFooter = styled.div`
  margin-top: ${spacing.md};
  font-size: 13px;
  color: ${colors.gray600};
  font-weight: 500;
  text-align: center;
  padding: ${spacing.sm} ${spacing.lg};
  background: ${colors.gray50};
  border-radius: ${borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${spacing.sm};
`;

const ClarificationContainer = styled.div`
  margin-top: ${spacing.lg};
  background: rgba(0, 51, 255, 0.03);
  border-radius: ${borderRadius.lg};
  padding: ${spacing.xl};
  border: 2px solid ${colors.primary};
  max-width: 100%;
`;

const ClarificationTitle = styled.h4`
  margin: 0 0 ${spacing.lg} 0;
  color: ${colors.black};
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
`;

const QuestionsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0 0 ${spacing.lg} 0;
`;

const QuestionItem = styled.li`
  padding: ${spacing.md} ${spacing.lg};
  margin-bottom: ${spacing.sm};
  background: ${colors.white};
  border-radius: ${borderRadius.md};
  border-left: 4px solid ${colors.warning};
  color: ${colors.black};
  font-weight: 500;
  font-size: 14px;
  box-shadow: ${shadows.sm};

  &::before {
    content: '•';
    color: ${colors.warning};
    font-weight: bold;
    margin-right: ${spacing.sm};
  }
`;

const SuggestionsTitle = styled.h5`
  margin: ${spacing.lg} 0 ${spacing.md} 0;
  color: ${colors.gray600};
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
`;

const SuggestionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${spacing.sm};
`;

const SuggestionItem = styled.div`
  padding: ${spacing.md} ${spacing.lg};
  background: ${colors.white};
  border-radius: ${borderRadius.md};
  border: 2px solid ${colors.gray200};
  color: ${colors.black};
  font-size: 14px;
  line-height: 1.5;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: ${shadows.sm};

  &:hover {
    border-color: ${colors.primary};
    background: ${colors.gray50};
    transform: translateX(4px);
  }

  &::before {
    content: '→';
    color: ${colors.primary};
    font-weight: bold;
    margin-right: ${spacing.sm};
  }
`;

const ErrorContainer = styled.div`
  margin-top: ${spacing.lg};
  background: rgba(239, 68, 68, 0.05);
  border-radius: ${borderRadius.lg};
  padding: ${spacing.xl};
  border: 2px solid ${colors.error};
  max-width: 100%;
`;

const ErrorTitle = styled.h4`
  margin: 0 0 ${spacing.md} 0;
  color: ${colors.error};
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
`;

const ErrorMessage = styled.p`
  margin: 0 0 ${spacing.md} 0;
  color: ${colors.black};
  font-size: 14px;
  line-height: 1.6;
`;

const ErrorDetails = styled.details`
  margin-top: ${spacing.md};
  padding: ${spacing.md};
  background: rgba(239, 68, 68, 0.05);
  border-radius: ${borderRadius.md};
  cursor: pointer;

  summary {
    font-weight: 600;
    color: ${colors.error};
    font-size: 13px;
    user-select: none;

    &:hover {
      color: ${colors.error};
      filter: brightness(1.1);
    }
  }

  pre {
    margin: ${spacing.md} 0 0 0;
    padding: ${spacing.md};
    background: #FEF2F2;
    border-radius: ${borderRadius.sm};
    overflow-x: auto;
    font-size: 12px;
    color: #991B1B;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
`;

const ChatMessage = ({ message, onSuggestionClick, onSaveQuery }) => {
  const [showData, setShowData] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

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

  const handleGenerateReport = async () => {
    if (!message.data || !message.data.csv_filename) {
      alert('No CSV data available for analysis');
      return;
    }

    setIsGeneratingReport(true);

    try {
      // Download the CSV content first
      const csvResponse = await axios.get(`/api/download/${message.data.csv_filename}`, {
        responseType: 'text'
      });

      // Send to analyst agent API (CSV only, no query)
      const analystResponse = await axios.post('http://localhost:8502/upload-csv', {
        csv_content: csvResponse.data,
        filename: message.data.csv_filename
      });

      if (analystResponse.data.success) {
        // Open Streamlit app in new tab
        window.open(analystResponse.data.streamlit_url, '_blank');

        alert('CSV uploaded to analyst! The Streamlit app has opened in a new tab.');
      } else {
        alert(`Failed to upload CSV: ${analystResponse.data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert(`Error generating report: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleSaveQuery = () => {
    if (!message.data || !message.text) {
      alert('Unable to save query - missing data');
      return;
    }

    if (isSaved) {
      return; // Already saved
    }

    // Create query object to save
    const queryToSave = {
      id: message.id,
      name: message.text.length > 60 ? message.text.substring(0, 57) + '...' : message.text,
      description: message.data.description || message.text,
      dateSaved: new Date().toISOString(),
      rowCount: message.data.row_count || null,
      csvFilename: message.data.csv_filename || null
    };

    // Call parent handler to save query
    if (onSaveQuery) {
      onSaveQuery(queryToSave);
      setIsSaved(true);
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

      {/* Show clarification UI for clarification responses */}
      {message.sender === 'assistant' && message.responseType === 'clarification' && message.data && (
        <ClarificationContainer>
          <ClarificationTitle>I need some clarification</ClarificationTitle>

          {message.data.data?.clarification_questions && message.data.data.clarification_questions.length > 0 && (
            <>
              <QuestionsList>
                {message.data.data.clarification_questions.map((question, index) => (
                  <QuestionItem key={index}>{question}</QuestionItem>
                ))}
              </QuestionsList>
            </>
          )}

          {message.data.data?.suggestions && message.data.data.suggestions.length > 0 && (
            <>
              <SuggestionsTitle>Example queries</SuggestionsTitle>
              <SuggestionsList>
                {message.data.data.suggestions.map((suggestion, index) => (
                  <SuggestionItem
                    key={index}
                    onClick={() => onSuggestionClick && onSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </SuggestionItem>
                ))}
              </SuggestionsList>
            </>
          )}
        </ClarificationContainer>
      )}

      {/* Show results for successful data result responses */}
      {message.sender === 'assistant' && message.responseType === 'data_result' && message.data && !message.isError && (
        <ResultsContainer>
          <ResultsHeader>
            <ResultsTitle>
              Query Results
              {message.data.row_count && ` (${message.data.row_count} rows)`}
            </ResultsTitle>
            {message.data.csv_filename && (
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <SaveQueryButton
                  onClick={handleSaveQuery}
                  disabled={isSaved}
                  className={isSaved ? 'saved' : ''}
                >
                  {isSaved ? '✓ Saved' : 'Save Query'}
                </SaveQueryButton>
                <DownloadButton onClick={handleDownloadCSV}>
                  Download CSV
                </DownloadButton>
                <GenerateReportButton
                  onClick={handleGenerateReport}
                  disabled={isGeneratingReport}
                >
                  {isGeneratingReport ? 'Uploading...' : 'Generate Report'}
                </GenerateReportButton>
              </div>
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

      {/* Show error UI for error responses */}
      {message.isError && (
        <ErrorContainer>
          <ErrorTitle>Error Processing Query</ErrorTitle>
          <ErrorMessage>{message.text}</ErrorMessage>
          {message.data?.details && (
            <ErrorDetails>
              <summary>Technical Details (for debugging)</summary>
              <pre>{typeof message.data.details === 'string' ? message.data.details : JSON.stringify(message.data.details, null, 2)}</pre>
            </ErrorDetails>
          )}
        </ErrorContainer>
      )}
    </MessageContainer>
  );
};

export default ChatMessage;