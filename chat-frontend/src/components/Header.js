import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius, spacing } from '../theme/weezeventTheme';

const HeaderContainer = styled.header`
  background: ${colors.primary};
  color: ${colors.white};
  padding: ${spacing.lg} ${spacing.xl};
  box-shadow: ${shadows.md};
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid ${colors.primaryDark};
`;

const HeaderContent = styled.div`
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const BrandContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.md};
`;

const Logo = styled.div`
  width: 36px;
  height: 36px;
  background: ${colors.white};
  border-radius: ${borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: ${colors.primary};
  box-shadow: ${shadows.sm};
`;

const TitleContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const Title = styled.h1`
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: ${colors.white};
  letter-spacing: -0.3px;
`;

const Subtitle = styled.p`
  font-size: 13px;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
`;

const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.md};
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  padding: ${spacing.sm} ${spacing.lg};
  background: rgba(255, 255, 255, 0.15);
  color: ${colors.white};
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: ${borderRadius.full};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-1px);
    box-shadow: ${shadows.md};
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
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

const StatusBadge = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  font-size: 13px;
  background: rgba(16, 185, 129, 0.15);
  color: ${colors.white};
  padding: ${spacing.sm} ${spacing.md};
  border-radius: ${borderRadius.full};
  font-weight: 600;
  border: 1px solid rgba(16, 185, 129, 0.3);

  .status-dot {
    width: 8px;
    height: 8px;
    background-color: ${colors.success};
    border-radius: ${borderRadius.full};
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    50% {
      box-shadow: 0 0 0 4px rgba(16, 185, 129, 0);
    }
  }
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
        <BrandContainer>
          <Logo>W</Logo>
          <TitleContainer>
            <Title>Weezagent Analyst</Title>
            <Subtitle>Smart Event Analytics</Subtitle>
          </TitleContainer>
        </BrandContainer>
        <HeaderActions>
          <RefreshButton
            onClick={handleRefreshMetadata}
            disabled={isRefreshing}
            title="Refresh Cube metadata and system context"
          >
            <span className="refresh-icon">↻</span>
            {isRefreshing ? 'Refreshing...' : refreshMessage || 'Refresh'}
          </RefreshButton>
          <StatusBadge>
            <div className="status-dot"></div>
            Online
          </StatusBadge>
        </HeaderActions>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;