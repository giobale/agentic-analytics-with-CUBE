import React from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius, spacing } from '../theme/weezeventTheme';

const TabsContainer = styled.div`
  background: ${colors.white};
  border-bottom: 2px solid ${colors.gray200};
  position: sticky;
  top: 73px;
  z-index: 99;
  box-shadow: ${shadows.sm};
`;

const TabsWrapper = styled.div`
  max-width: 1360px;
  margin: 0 auto;
  padding: 0 ${spacing.xl};
  display: flex;
  justify-content: center;
  align-items: center;
  gap: ${spacing['4xl']};
`;

const Tab = styled.button`
  flex: 0 0 auto;
  padding: ${spacing.lg} ${spacing.xl};
  border: none;
  background: transparent;
  color: ${props => props.active ? colors.primary : colors.gray600};
  font-size: 15px;
  font-weight: ${props => props.active ? 700 : 500};
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;

  &:hover {
    color: ${colors.primary};
    background: rgba(0, 51, 255, 0.03);
  }

  ${props => props.active && `
    color: ${colors.primary};
    border-bottom-color: ${colors.primary};
  `}

  &:focus {
    outline: none;
    box-shadow: inset 0 0 0 2px rgba(0, 51, 255, 0.2);
  }
`;

const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'chat', label: 'Chat' },
    { id: 'saved-queries', label: 'Saved Queries' },
    { id: 'metrics-catalog', label: 'Metrics Catalog' }
  ];

  return (
    <TabsContainer>
      <TabsWrapper>
        {tabs.map(tab => (
          <Tab
            key={tab.id}
            active={activeTab === tab.id}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </Tab>
        ))}
      </TabsWrapper>
    </TabsContainer>
  );
};

export default TabNavigation;
