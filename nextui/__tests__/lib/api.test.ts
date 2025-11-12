import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getSongs, getArtist, getArtists } from '@/lib/api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API functions', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('getSongs', () => {
    it('fetches songs successfully', async () => {
      const mockSongs = [
        { id: 1, title: 'Test Song', artistId: 1, releaseDate: '2024-01-01', url: 'http://test.com' },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSongs,
      });

      const result = await getSongs();
      expect(result).toEqual(mockSongs);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/v1/songs'),
        expect.objectContaining({ cache: 'no-store' })
      );
    });

    it('throws error when fetch fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      });

      await expect(getSongs()).rejects.toThrow('Failed to fetch songs: Not Found');
    });
  });

  describe('getArtist', () => {
    it('fetches artist successfully', async () => {
      const mockArtist = { id: 1, name: 'Test Artist' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockArtist,
      });

      const result = await getArtist(1);
      expect(result).toEqual(mockArtist);
    });

    it('returns null when artist not found', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      });

      const result = await getArtist(999);
      expect(result).toBeNull();
    });
  });

  describe('getArtists', () => {
    it('fetches multiple artists', async () => {
      const mockArtists = [
        { id: 1, name: 'Artist 1' },
        { id: 2, name: 'Artist 2' },
      ];

      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockArtists[0],
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockArtists[1],
        });

      const result = await getArtists([1, 2]);
      expect(result.size).toBe(2);
      expect(result.get(1)).toEqual(mockArtists[0]);
      expect(result.get(2)).toEqual(mockArtists[1]);
    });
  });
});
