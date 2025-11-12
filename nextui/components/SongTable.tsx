'use client';

/**
 * Client Component that renders the song table
 */

import { SongWithArtist } from '@/types';

interface SongTableProps {
  songs: SongWithArtist[];
}

export default function SongTable({ songs }: SongTableProps) {
  return (
    <div className="w-full max-w-4xl mx-auto px-4">
      <div className="bg-[#0D0938]/70 backdrop-blur-sm rounded-lg shadow-2xl overflow-hidden border border-[#FFFACD]/20">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-[#FFFACD]">
              <th className="px-6 py-4 text-left text-xl font-semibold">Song</th>
              <th className="px-6 py-4 text-left text-xl font-semibold">Artist</th>
            </tr>
          </thead>
          <tbody>
            {songs.map((song) => (
              <tr
                key={song.id}
                className="border-b border-[#FFFACD]/20 hover:bg-[#FFFACD]/10 transition-colors duration-200"
              >
                <td className="px-6 py-4">
                  <a
                    href={song.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#FFFACD] hover:text-white hover:shadow-[0_0_8px_#FFFACD] transition-all duration-300 text-lg"
                  >
                    {song.title}
                  </a>
                </td>
                <td className="px-6 py-4 text-[#FFFACD] text-lg">{song.artistName}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
