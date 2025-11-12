/**
 * Type definitions for Accessible application
 */

export interface Song {
  id: number;
  title: string;
  artist_id: number;
  release_date: string;
  url: string;
  distance?: number;
}

export interface Artist {
  id: number;
  name: string;
}

export interface SongWithArtist extends Song {
  artist_name: string;
}
