/**
 * Loading spinner component
 */

export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="relative w-16 h-16">
        <div className="absolute top-0 left-0 w-full h-full border-4 border-[#FFFACD]/30 rounded-full"></div>
        <div className="absolute top-0 left-0 w-full h-full border-4 border-[#FFFACD] border-t-transparent rounded-full animate-spin"></div>
      </div>
      <p className="ml-4 text-[#FFFACD] text-xl">Loading songs...</p>
    </div>
  );
}
