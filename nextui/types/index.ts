/**
 * Type definitions for Star Songs application
 */

export interface Song {
  id: number;
  title: string;
  artistId: number;
  releaseDate: string;
  url: string;
  distance?: number;
}

export interface Artist {
  id: number;
  name: string;
}

export interface SongWithArtist extends Song {
  artistName: string;
}
