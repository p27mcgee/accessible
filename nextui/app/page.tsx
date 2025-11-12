import { Suspense } from 'react';
import SongList from '@/components/SongList';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function Home() {
  return (
    <main className="min-h-screen py-12 flex flex-col items-center">
      <h1 className="text-5xl font-bold text-center mb-12 text-[#FFFACD] drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
        Star Songs
      </h1>
      <Suspense fallback={<LoadingSpinner />}>
        <SongList />
      </Suspense>
    </main>
  );
}
