import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius, spacing } from '../theme/weezeventTheme';

const InputContainer = styled.div`
  padding: ${spacing.xl} 0;
  background-color: ${colors.white};
  border-top: 1px solid ${colors.gray200};
  position: sticky;
  bottom: 0;
`;

const InputForm = styled.form`
  display: flex;
  gap: ${spacing.md};
  align-items: flex-end;
`;

const TextInputContainer = styled.div`
  flex: 1;
  position: relative;
`;

const TextInput = styled.textarea`
  width: 100%;
  min-height: 48px;
  max-height: 120px;
  padding: ${spacing.md} ${spacing.lg};
  padding-right: 60px;
  border: 2px solid ${colors.gray300};
  border-radius: ${borderRadius.lg};
  font-size: 15px;
  line-height: 1.5;
  resize: none;
  outline: none;
  font-family: inherit;
  color: ${colors.black};
  background-color: ${colors.white};
  transition: all 0.2s ease;

  &:focus {
    border-color: ${colors.primary};
    box-shadow: 0 0 0 3px rgba(0, 51, 255, 0.1);
  }

  &:disabled {
    background-color: ${colors.gray100};
    cursor: not-allowed;
    border-color: ${colors.gray200};
  }

  &::placeholder {
    color: ${colors.gray400};
  }
`;

const SendButton = styled.button`
  width: 48px;
  height: 48px;
  border-radius: ${borderRadius.full};
  border: none;
  background-color: ${colors.primary};
  color: ${colors.white};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  box-shadow: ${shadows.md};

  &:hover:not(:disabled) {
    background-color: ${colors.primaryDark};
    transform: scale(1.05);
    box-shadow: ${shadows.primary};
  }

  &:active:not(:disabled) {
    transform: scale(0.95);
  }

  &:disabled {
    background-color: ${colors.gray400};
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  svg {
    width: 22px;
    height: 22px;
  }
`;

const CharacterCount = styled.div`
  position: absolute;
  bottom: ${spacing.sm};
  right: ${spacing.md};
  font-size: 11px;
  color: ${colors.gray500};
  pointer-events: none;
  background: ${colors.white};
  padding: 2px ${spacing.xs};
  border-radius: ${borderRadius.sm};
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