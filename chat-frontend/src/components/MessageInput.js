import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

const colors = {
  primary: '#1976D2',      // Royal Blue
  success: '#7ED321',      // Bright Green
  white: '#FFFFFF',        // White
  background: '#F5F5F5',   // Light Gray
  textPrimary: '#333333',  // Dark Gray
  textSecondary: '#666666' // Medium Gray
};

const InputContainer = styled.div`
  padding: 20px 0;
  background-color: ${colors.white};
  border-top: 1px solid #e0e0e0;
  position: sticky;
  bottom: 0;
`;

const InputForm = styled.form`
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

const TextInputContainer = styled.div`
  flex: 1;
  position: relative;
`;

const TextInput = styled.textarea`
  width: 100%;
  min-height: 44px;
  max-height: 120px;
  padding: 12px 16px;
  padding-right: 50px;
  border: 2px solid #e0e0e0;
  border-radius: 22px;
  font-size: 14px;
  line-height: 1.4;
  resize: none;
  outline: none;
  font-family: inherit;
  color: ${colors.textPrimary};
  background-color: ${colors.white};
  transition: border-color 0.2s ease;

  &:focus {
    border-color: ${colors.primary};
  }

  &:disabled {
    background-color: ${colors.background};
    cursor: not-allowed;
  }

  &::placeholder {
    color: ${colors.textSecondary};
  }
`;

const SendButton = styled.button`
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background-color: ${colors.primary};
  color: ${colors.white};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;

  &:hover:not(:disabled) {
    background-color: #1565C0;
    transform: scale(1.05);
  }

  &:disabled {
    background-color: ${colors.textSecondary};
    cursor: not-allowed;
    transform: none;
  }

  svg {
    width: 20px;
    height: 20px;
  }
`;

const CharacterCount = styled.div`
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 11px;
  color: ${colors.textSecondary};
  pointer-events: none;
`;

const MessageInput = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);
  const maxLength = 500;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
    }
  };

  const canSend = message.trim().length > 0 && !disabled;

  return (
    <InputContainer>
      <InputForm onSubmit={handleSubmit}>
        <TextInputContainer>
          <TextInput
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={disabled ? "Processing your query..." : "Ask me anything about your event data..."}
            disabled={disabled}
            rows={1}
          />
          <CharacterCount>
            {message.length}/{maxLength}
          </CharacterCount>
        </TextInputContainer>

        <SendButton
          type="submit"
          disabled={!canSend}
          title="Send message"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22,2 15,22 11,13 2,9" />
          </svg>
        </SendButton>
      </InputForm>
    </InputContainer>
  );
};

export default MessageInput;