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

/**
 * Pagination metadata returned by the API
 */
export interface PaginationMetadata {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationMetadata;
}
