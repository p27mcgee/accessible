/**
 * API client for SongData service
 */

import { Song, Artist } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_SONGDATA_API_URL || 'http://localhost:8086';

/**
 * Fetch all songs from the songdata API
 */
export async function getSongs(): Promise<Song[]> {
  const response = await fetch(`${API_BASE_URL}/v1/songs`, {
    cache: 'no-store', // Always fetch fresh data
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch songs: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch a specific artist by ID
 */
export async function getArtist(id: number): Promise<Artist | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/artists/${id}`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      console.warn(`Artist ${id} not found: ${response.statusText}`);
      return null;
    }

    return response.json();
  } catch (error) {
    console.error(`Error fetching artist ${id}:`, error);
    return null;
  }
}

/**
 * Fetch multiple artists by their IDs
 */
export async function getArtists(ids: number[]): Promise<Map<number, Artist>> {
  const artistMap = new Map<number, Artist>();

  await Promise.all(
    ids.map(async (id) => {
      const artist = await getArtist(id);
      if (artist) {
        artistMap.set(id, artist);
      }
    })
  );

  return artistMap;
}
