# AI-Powered Testing Platform - Frontend

A modern React.js frontend for the AI-powered data profiling and testing platform, built with React 19.1, TypeScript, and Tailwind CSS 4.1.

## Features

- **Modern UI**: Built with React 19.1 and Tailwind CSS 4.1
- **Real-time Updates**: WebSocket integration for live data
- **Data Profiling**: Interactive forms for database metadata analysis
- **Responsive Design**: Mobile-first responsive layout
- **TypeScript**: Full type safety and IntelliSense support
- **Fast Development**: Vite-powered development server

## Tech Stack

- React 19.1
- TypeScript 5.7
- Tailwind CSS 4.1
- Vite 6.0
- Axios for API calls
- Lucide React for icons

## Prerequisites

- Node.js >= 22.16.0
- npm or yarn
- Running backend API at `http://localhost:8100`

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run format` - Format code with Prettier
- `npm run type-check` - Type check without emitting

## Backend Integration

The frontend connects to the FastAPI backend running on port 8100:

- **API Endpoints**: Proxied through Vite dev server
- **WebSocket**: Real-time communication for live updates
- **CORS**: Configured for cross-origin requests

### API Endpoints Used

- `GET /metadata` - Get database table metadata
- `GET /api/endpoints` - Get available API endpoints
- `WebSocket /ws/{client_id}` - Real-time updates

## Project Structure

```
src/
├── components/          # React components
│   ├── DataProfiler.tsx # Main data profiling interface
│   ├── Header.tsx       # Application header
│   ├── StatusBar.tsx    # Connection status bar
│   ├── FormInput.tsx    # Reusable form input
│   └── LoadingSpinner.tsx # Loading indicator
├── services/            # API and WebSocket services
│   └── api.ts          # API client and WebSocket service
├── types/              # TypeScript type definitions
│   └── api.ts          # API-related types
├── App.tsx             # Main application component
├── main.tsx            # Application entry point
└── index.css           # Global styles and Tailwind imports
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8100
VITE_WS_URL=ws://localhost:8100
```

## Development Features

- **Hot Module Replacement**: Instant updates during development
- **Proxy Configuration**: Automatic API proxying to backend
- **TypeScript Support**: Full type checking and IntelliSense
- **ESLint & Prettier**: Code linting and formatting
- **Tailwind CSS**: Utility-first CSS framework

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready for deployment.

## WebSocket Integration

The application maintains a persistent WebSocket connection for:

- Real-time connection status updates
- Live user activity notifications
- Form submission notifications
- System health monitoring

## Styling

This project uses Tailwind CSS 4.1 with:

- Custom color palette based on the original design
- Responsive utilities for mobile-first design
- Custom component classes for consistency
- Smooth animations and transitions

## License

MIT License - see the LICENSE file for details.
