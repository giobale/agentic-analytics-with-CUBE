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

const Subtitle = styled.p`
  font-size: 16px;
  color: ${colors.gray600};
  margin: 0;
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

const QueryCard = styled.div`
  background: ${colors.white};
  border: 2px solid ${colors.gray200};
  border-radius: ${borderRadius.lg};
  padding: ${spacing.xl};
  box-shadow: ${shadows.sm};
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 180px;

  &:hover {
    border-color: ${colors.primary};
    box-shadow: ${shadows.primary};
    transform: translateY(-2px);
  }
`;

const QueryName = styled.h3`
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

const QueryDescription = styled.p`
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

const QueryMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: ${colors.gray500};
  padding-top: ${spacing.md};
  border-top: 1px solid ${colors.gray200};
  margin-top: ${spacing.md};
`;

const DateSaved = styled.span`
  font-weight: 500;
`;

const RowCount = styled.span`
  background: ${colors.gray100};
  padding: ${spacing.xs} ${spacing.sm};
  border-radius: ${borderRadius.sm};
  font-weight: 600;
  color: ${colors.gray700};
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

const GridWrapper = styled.div`
  role: list;
`;

const SavedQueries = ({ savedQueries = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredQueries = useMemo(() => {
    if (!searchTerm.trim()) {
      return savedQueries;
    }

    const lowerSearch = searchTerm.toLowerCase();
    return savedQueries.filter(query =>
      query.name.toLowerCase().includes(lowerSearch) ||
      query.description.toLowerCase().includes(lowerSearch)
    );
  }, [savedQueries, searchTerm]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  return (
    <Container>
      <Header>
        <Title>Saved Datasets</Title>
        <Subtitle>
          Your saved datasets are ready to use anytime
        </Subtitle>
      </Header>

      {savedQueries.length > 0 && (
        <SearchContainer>
          <SearchInput
            type="text"
            placeholder="Search…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            aria-label="Search"
          />
        </SearchContainer>
      )}

      {savedQueries.length === 0 ? (
        <EmptyState role="status" aria-live="polite">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
          </svg>
          <h3>No datasets saved yet</h3>
          <p>
            You haven't saved any queries yet. Save a query from the Chat tab.
          </p>
        </EmptyState>
      ) : (
        <>
          {searchTerm && (
            <ResultsCount role="status" aria-live="polite">
              {filteredQueries.length} {filteredQueries.length === 1 ? 'result' : 'results'} found
            </ResultsCount>
          )}

          {filteredQueries.length === 0 ? (
            <EmptyState role="status" aria-live="polite">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <h3>No matching queries found</h3>
              <p>Try adjusting your search terms</p>
            </EmptyState>
          ) : (
            <Grid role="list" aria-label="Saved datasets">
              {filteredQueries.map(query => (
                <QueryCard key={query.id} role="listitem">
                  <QueryName>{query.name}</QueryName>
                  <QueryMeta>
                    <DateSaved>Saved on {new Date(query.dateSaved).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</DateSaved>
                    {query.rowCount && (
                      <RowCount>{query.rowCount} rows</RowCount>
                    )}
                  </QueryMeta>
                </QueryCard>
              ))}
            </Grid>
          )}
        </>
      )}
    </Container>
  );
};

export default SavedQueries;
