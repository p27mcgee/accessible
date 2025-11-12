# Star Songs - Next.js Frontend

Modern Next.js 16 frontend for the Star Songs application, showcasing celestial-themed music.

## Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS 4
- **Testing**: Vitest + React Testing Library
- **Architecture**: React Server Components + Client Components
- **Build Tool**: Turbopack (Next.js native)

## Features

- ✨ Server-side data fetching with React Server Components
- 🎨 Starry night theme with responsive design
- 🔒 Type-safe API integration with TypeScript
- 🧪 Comprehensive test coverage with Vitest
- 🐳 Docker-ready with multi-stage builds
- ⚡ Fast development with Turbopack
- 📦 Optimized production builds with standalone output

## Getting Started

### Prerequisites

- Node.js 20.9.0+ (recommended: Node 20 LTS or Node 22 LTS)
- npm 10+
- SongData API running on port 8086

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The app will automatically reload when you make changes.

### Environment Variables

Create a `.env.local` file for local development:

```bash
NEXT_PUBLIC_SONGDATA_API_URL=http://localhost:8086
```

For production/Docker, use `.env.production` or Docker environment variables.

## Testing

```bash
# Run tests in watch mode
npm test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

## Building

### Development Build

```bash
npm run build
npm start
```

The app will be available at [http://localhost:3000](http://localhost:3000).

### Docker Build

```bash
docker build -t starsongs-nextui .
docker run -p 3000:3000 -e NEXT_PUBLIC_SONGDATA_API_URL=http://songdata:8086 starsongs-nextui
```

## Project Structure

```
nextui/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Home page
│   └── globals.css         # Global styles
├── components/             # React components
│   ├── SongList.tsx        # Server Component for fetching songs
│   ├── SongTable.tsx       # Client Component for rendering table
│   └── LoadingSpinner.tsx  # Loading state component
├── lib/                    # Utility functions
│   └── api.ts              # API client for SongData service
├── types/                  # TypeScript type definitions
│   └── index.ts            # Song, Artist, and related types
├── __tests__/              # Test files
│   ├── components/         # Component tests
│   └── lib/                # Library/utility tests
├── public/                 # Static assets
│   └── starry-night.png    # Background image
├── Dockerfile              # Multi-stage Docker build
├── vitest.config.ts        # Vitest configuration
├── next.config.ts          # Next.js configuration
├── tailwind.config.ts      # TailwindCSS configuration
└── tsconfig.json           # TypeScript configuration
```

## Architecture

### Data Flow

```
User Request → Next.js Server
              ↓
       SongList (Server Component)
              ↓
       API Client (lib/api.ts)
              ↓
       SongData REST API (port 8086)
              ↓
       SongTable (Client Component)
              ↓
       Browser DOM
```

### Component Strategy

- **Server Components** (`SongList.tsx`): Fetch data on the server for better performance and SEO
- **Client Components** (`SongTable.tsx`): Handle interactivity and browser-only features
- **Suspense Boundaries**: Graceful loading states with `LoadingSpinner`

## API Integration

The app communicates directly with the SongData API:

- `GET /v1/songs` - Fetch all songs
- `GET /v1/artists/{id}` - Fetch artist by ID

API calls are made from Server Components for optimal performance.

## Styling

TailwindCSS 4 with custom theme colors:

- Background: `#0D0938` (deep night blue)
- Foreground: `#FFFACD` (lemon chiffon)
- Custom starry night background image

## Performance Optimizations

- Server-side data fetching (reduces client bundle size)
- Standalone output mode for minimal Docker images
- Image optimization with Next.js Image component
- Turbopack for fast development builds
- Production optimizations (minification, tree-shaking)

## Contributing

1. Write tests for new features
2. Ensure all tests pass: `npm test`
3. Follow TypeScript best practices
4. Use Server Components by default, Client Components only when needed

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [TailwindCSS](https://tailwindcss.com/docs)
- [Vitest](https://vitest.dev/)
