import React from 'react';
import styled from 'styled-components';

const colors = {
  primary: '#1976D2',
  white: '#FFFFFF',
  textPrimary: '#333333'
};

const HeaderContainer = styled.header`
  background-color: ${colors.primary};
  color: ${colors.white};
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
`;

const HeaderContent = styled.div`
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Subtitle = styled.p`
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
`;

const Logo = styled.div`
  width: 32px;
  height: 32px;
  background-color: ${colors.white};
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: ${colors.primary};
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;

  .status-dot {
    width: 8px;
    height: 8px;
    background-color: #7ED321;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(126, 211, 33, 0.7);
    }
    70% {
      box-shadow: 0 0 0 6px rgba(126, 211, 33, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(126, 211, 33, 0);
    }
  }
`;

const Header = () => {
  return (
    <HeaderContainer>
      <HeaderContent>
        <div>
          <Title>
            <Logo>C</Logo>
            CUBE Chat
          </Title>
          <Subtitle>Natural Language Query Interface</Subtitle>
        </div>
        <StatusIndicator>
          <div className="status-dot"></div>
          Connected
        </StatusIndicator>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;