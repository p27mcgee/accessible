/**
 * Server Component that displays the list of songs
 */

import { getSongs, getArtists } from '@/lib/api';
import { SongWithArtist } from '@/types';
import SongTable from './SongTable';

export default async function SongList() {
  try {
    // Fetch songs from the API (Server Side)
    const songs = await getSongs();

    // Get unique artist IDs
    const artistIds = Array.from(new Set(songs.map((song) => song.artistId)));

    // Fetch all artists
    const artistMap = await getArtists(artistIds);

    // Combine songs with artist names
    const songsWithArtists: SongWithArtist[] = songs.map((song) => ({
      ...song,
      artistName: artistMap.get(song.artistId)?.name || 'Unknown Artist',
    }));

    return <SongTable songs={songsWithArtists} />;
  } catch (error) {
    console.error('Error loading songs:', error);
    return (
      <div className="text-center py-12">
        <p className="text-red-400 text-xl">Error loading songs. Please try again later.</p>
      </div>
    );
  }
}
