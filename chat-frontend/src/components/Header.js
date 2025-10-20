import React, { useState } from 'react';
import styled from 'styled-components';

const colors = {
  primary: '#6366F1',      // Modern indigo - professional yet vibrant
  secondary: '#8B5CF6',    // Purple accent - creative energy
  white: '#FFFFFF',
  textPrimary: '#1F2937',  // Warm dark gray
  accent: '#F59E0B'        // Amber - represents success/insights
};

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, ${colors.primary} 0%, ${colors.secondary} 100%);
  color: ${colors.white};
  padding: 20px 24px;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const HeaderContent = styled.div`
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  letter-spacing: -0.5px;

  .brand-name {
    background: linear-gradient(45deg, ${colors.white} 0%, ${colors.accent} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

const Subtitle = styled.p`
  font-size: 15px;
  margin: 4px 0 0 0;
  opacity: 0.85;
  font-weight: 400;
  letter-spacing: 0.2px;
`;

const Logo = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, ${colors.white} 0%, ${colors.accent} 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
  position: relative;

  &::before {
    content: '';
    position: absolute;
    inset: 2px;
    background: ${colors.primary};
    border-radius: 10px;
    z-index: -1;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);

  .status-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
      box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
  }
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  color: ${colors.white};
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);

  &:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  .refresh-icon {
    display: inline-block;
    transition: transform 0.3s ease;
  }

  &:disabled .refresh-icon {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Header = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState('');

  const handleRefreshMetadata = async () => {
    setIsRefreshing(true);
    setRefreshMessage('');

    try {
      const orchestratorUrl = process.env.REACT_APP_ORCHESTRATOR_URL || 'http://localhost:8080';
      const response = await fetch(`${orchestratorUrl}/refresh-metadata`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Metadata refreshed:', data);
        setRefreshMessage('✅ Context refreshed!');

        // Clear success message after 3 seconds
        setTimeout(() => setRefreshMessage(''), 3000);
      } else {
        const errorData = await response.json();
        console.error('Refresh failed:', errorData);
        setRefreshMessage('❌ Refresh failed');
        setTimeout(() => setRefreshMessage(''), 3000);
      }
    } catch (error) {
      console.error('Error refreshing metadata:', error);
      setRefreshMessage('❌ Connection error');
      setTimeout(() => setRefreshMessage(''), 3000);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <div>
          <Title>
            <Logo>📊</Logo>
            <span className="brand-name">Weezagent Analyst</span>
          </Title>
          <Subtitle>🎯 Smart Event Analytics for Better Decisions</Subtitle>
        </div>
        <HeaderActions>
          <RefreshButton
            onClick={handleRefreshMetadata}
            disabled={isRefreshing}
            title="Refresh Cube metadata and system context"
          >
            <span className="refresh-icon">🔄</span>
            {isRefreshing ? 'Refreshing...' : refreshMessage || 'Refresh Context'}
          </RefreshButton>
          <StatusIndicator>
            <div className="status-dot"></div>
            🟢 AI Ready
          </StatusIndicator>
        </HeaderActions>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;