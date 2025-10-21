import React from 'react';
import styled from 'styled-components';
import { colors, shadows, borderRadius, spacing } from '../theme/weezeventTheme';

const Container = styled.div`
  max-width: 900px;
  margin: 0 auto;
  padding: ${spacing['3xl']} ${spacing.xl};
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

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: ${spacing.xl};

  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
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
  gap: ${spacing.md};
  position: relative;

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
  margin-bottom: ${spacing.sm};
`;

const MetricName = styled.h3`
  font-size: 17px;
  font-weight: 700;
  color: ${colors.black};
  margin: 0;
  line-height: 1.4;
`;

const MetricDescription = styled.p`
  font-size: 14px;
  color: ${colors.gray600};
  margin: 0;
  line-height: 1.5;
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
  margin-top: ${spacing.sm};
  align-self: flex-start;
`;

const MetricsCatalog = () => {
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

  return (
    <Container>
      <Header>
        <Title>Metrics Catalog</Title>
        <IntroText>
          Pre-defined metrics for quick, ready-to-use insights.
          Explore these curated analytics to better understand your event performance.
        </IntroText>
      </Header>

      <Grid>
        {metrics.map(metric => (
          <MetricCard key={metric.id} categoryColor={metric.categoryColor}>
            <MetricIcon categoryColor={metric.categoryColor}>
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
    </Container>
  );
};

export default MetricsCatalog;
