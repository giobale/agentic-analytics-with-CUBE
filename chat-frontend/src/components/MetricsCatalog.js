import React, { useState, useMemo } from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius, spacing } from '../theme/weezeventTheme';

const Container = styled.div`
  max-width: 1360px;
  margin: 0 auto;
  padding: ${spacing['3xl']} ${spacing.xl};
  min-width: 1024px;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: ${spacing['3xl']};
`;

const Title = styled.h2`
  font-size: 32px;
  font-weight: 700;
  color: ${colors.black};
  margin: 0 0 ${spacing.md} 0;
  letter-spacing: -0.5px;
`;

const IntroText = styled.p`
  font-size: 16px;
  color: ${colors.gray600};
  margin: 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
`;

const SearchContainer = styled.div`
  max-width: 600px;
  margin: 0 auto ${spacing['3xl']} auto;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: ${spacing.lg} ${spacing.xl};
  padding-left: 48px;
  border: 2px solid ${colors.gray300};
  border-radius: ${borderRadius.lg};
  font-size: 15px;
  outline: none;
  transition: all 0.2s ease;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cpath d='m21 21-4.35-4.35'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: ${spacing.lg} center;
  background-size: 20px 20px;

  &:focus {
    border-color: ${colors.primary};
    box-shadow: 0 0 0 3px rgba(0, 51, 255, 0.1);
  }

  &::placeholder {
    color: ${colors.gray400};
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: ${spacing.xl};
  margin-bottom: ${spacing.xl};

  @media (max-width: 1279px) {
    grid-template-columns: repeat(3, 1fr);
  }

  @media (max-width: 1023px) {
    overflow-x: auto;
  }
`;

const MetricCard = styled.div`
  background: ${colors.white};
  border: 2px solid ${colors.gray200};
  border-radius: ${borderRadius.lg};
  padding: ${spacing.xl};
  box-shadow: ${shadows.sm};
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
  min-height: 220px;

  &:hover {
    border-color: ${colors.primary};
    box-shadow: ${shadows.primary};
    transform: translateY(-2px);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: ${props => props.categoryColor || colors.primary};
    border-radius: ${borderRadius.lg} 0 0 ${borderRadius.lg};
  }
`;

const MetricIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: ${borderRadius.md};
  background: ${props => props.categoryColor ? `${props.categoryColor}15` : 'rgba(0, 51, 255, 0.1)'};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: ${spacing.md};
`;

const MetricName = styled.h3`
  font-size: 16px;
  font-weight: 700;
  color: ${colors.black};
  margin: 0 0 ${spacing.md} 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const MetricDescription = styled.p`
  font-size: 14px;
  color: ${colors.gray600};
  margin: 0 0 auto 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
`;

const MetricCategory = styled.div`
  display: inline-flex;
  align-items: center;
  gap: ${spacing.xs};
  padding: ${spacing.xs} ${spacing.md};
  background: ${props => props.categoryColor ? `${props.categoryColor}15` : 'rgba(0, 51, 255, 0.1)'};
  color: ${props => props.categoryColor || colors.primary};
  border-radius: ${borderRadius.full};
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: ${spacing.md};
  align-self: flex-start;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${spacing['4xl']} ${spacing.xl};
  color: ${colors.gray500};
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  svg {
    width: 80px;
    height: 80px;
    margin: 0 auto ${spacing.xl} auto;
    opacity: 0.3;
  }

  h3 {
    font-size: 20px;
    font-weight: 600;
    color: ${colors.gray700};
    margin: 0 0 ${spacing.md} 0;
  }

  p {
    font-size: 15px;
    color: ${colors.gray600};
    margin: 0;
    line-height: 1.6;
  }
`;

const ResultsCount = styled.div`
  text-align: center;
  font-size: 14px;
  color: ${colors.gray600};
  margin-bottom: ${spacing.lg};
  font-weight: 500;
`;

const MetricsCatalog = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const metrics = [
    {
      id: 1,
      name: 'Weekly Revenue by Event',
      description: 'Track revenue performance for each event on a weekly basis to identify trends and patterns.',
      category: 'Revenue',
      icon: '💰',
      categoryColor: '#10B981'
    },
    {
      id: 2,
      name: 'Weekly Conversion Rate by Shop',
      description: 'Monitor how effectively each shop converts visitors into customers week over week.',
      category: 'Conversion',
      icon: '📊',
      categoryColor: '#3B82F6'
    },
    {
      id: 3,
      name: 'Revenue by Visitor City',
      description: 'Understand geographic distribution of revenue to optimize regional marketing strategies.',
      category: 'Geography',
      icon: '🗺️',
      categoryColor: '#8B5CF6'
    },
    {
      id: 4,
      name: 'Revenue per Visitor by Event',
      description: 'Measure average spending per visitor for each event to assess event profitability.',
      category: 'Revenue',
      icon: '💵',
      categoryColor: '#10B981'
    },
    {
      id: 5,
      name: 'Revenue by Age Group',
      description: 'Analyze purchasing behavior across different age demographics for targeted campaigns.',
      category: 'Demographics',
      icon: '👥',
      categoryColor: '#F59E0B'
    },
    {
      id: 6,
      name: 'Daily Ticket Sales Trends',
      description: 'Monitor daily ticket sales volume to identify peak selling periods and optimize inventory.',
      category: 'Sales',
      icon: '🎫',
      categoryColor: '#EF4444'
    }
  ];

  const filteredMetrics = useMemo(() => {
    if (!searchTerm.trim()) {
      return metrics;
    }

    const lowerSearch = searchTerm.toLowerCase();
    return metrics.filter(metric =>
      metric.name.toLowerCase().includes(lowerSearch) ||
      metric.description.toLowerCase().includes(lowerSearch)
    );
  }, [searchTerm]);

  return (
    <Container>
      <Header>
        <Title>Metrics Catalog</Title>
        <IntroText>
          Pre-defined metrics for quick, ready-to-use insights.
        </IntroText>
      </Header>

      <SearchContainer>
        <SearchInput
          type="text"
          placeholder="Search…"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          aria-label="Search metrics"
        />
      </SearchContainer>

      {searchTerm && (
        <ResultsCount role="status" aria-live="polite">
          {filteredMetrics.length} {filteredMetrics.length === 1 ? 'result' : 'results'} found
        </ResultsCount>
      )}

      {filteredMetrics.length === 0 ? (
        <EmptyState role="status" aria-live="polite">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <h3>No metrics found</h3>
          <p>Try adjusting your search terms</p>
        </EmptyState>
      ) : (
        <Grid role="list" aria-label="Metrics catalog">
          {filteredMetrics.map(metric => (
            <MetricCard key={metric.id} categoryColor={metric.categoryColor} role="listitem">
              <MetricIcon categoryColor={metric.categoryColor} aria-hidden="true">
                {metric.icon}
              </MetricIcon>
              <MetricName>{metric.name}</MetricName>
              <MetricDescription>{metric.description}</MetricDescription>
              <MetricCategory categoryColor={metric.categoryColor}>
                {metric.category}
              </MetricCategory>
            </MetricCard>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default MetricsCatalog;
