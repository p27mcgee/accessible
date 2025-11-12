import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import SongTable from '@/components/SongTable';
import { SongWithArtist } from '@/types';

describe('SongTable', () => {
  const mockSongs: SongWithArtist[] = [
    {
      id: 1,
      title: 'Fly Me to the Moon',
      artistId: 1,
      artistName: 'Frank Sinatra',
      releaseDate: '1964-01-01',
      url: 'https://www.youtube.com/watch?v=ZEcqHA7dbwM',
    },
    {
      id: 2,
      title: 'Rocket Man',
      artistId: 2,
      artistName: 'Elton John',
      releaseDate: '1972-04-14',
      url: 'https://www.youtube.com/watch?v=DtVBCG6ThDk',
    },
  ];

  it('renders song titles', () => {
    render(<SongTable songs={mockSongs} />);

    expect(screen.getByText('Fly Me to the Moon')).toBeInTheDocument();
    expect(screen.getByText('Rocket Man')).toBeInTheDocument();
  });

  it('renders artist names', () => {
    render(<SongTable songs={mockSongs} />);

    expect(screen.getByText('Frank Sinatra')).toBeInTheDocument();
    expect(screen.getByText('Elton John')).toBeInTheDocument();
  });

  it('renders song links with correct URLs', () => {
    render(<SongTable songs={mockSongs} />);

    const flyMeLink = screen.getByText('Fly Me to the Moon').closest('a');
    expect(flyMeLink).toHaveAttribute('href', 'https://www.youtube.com/watch?v=ZEcqHA7dbwM');
    expect(flyMeLink).toHaveAttribute('target', '_blank');
    expect(flyMeLink).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('renders table headers', () => {
    render(<SongTable songs={mockSongs} />);

    expect(screen.getByText('Song')).toBeInTheDocument();
    expect(screen.getByText('Artist')).toBeInTheDocument();
  });

  it('renders empty table when no songs provided', () => {
    render(<SongTable songs={[]} />);

    expect(screen.getByText('Song')).toBeInTheDocument();
    expect(screen.getByText('Artist')).toBeInTheDocument();
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });
});
