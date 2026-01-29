# HyperVolt Website - Frontend Module 4

## Overview

The HyperVolt website is a cutting-edge, real-time energy management dashboard built with Next.js, React Three Fiber, and WebSockets. It provides an immersive interface for visualizing and controlling the HyperVolt AI-Driven Energy Orchestrator system.

## Features

### 🎨 Mind-Blowing Visualizations

- **3D Digital Twin**: Interactive 3D room model with real-time lighting effects
- **Energy Flow Diagram**: Animated visualization showing power flowing from Solar/Battery/Grid to your home
- **Real-time Charts**: Energy forecast charts comparing AI predictions with actual usage
- **Live Stats**: Dynamic cards showing carbon savings, cost savings, and system efficiency

### 🧠 AI Strategy Narrator

- Real-time log of AI decisions and system events
- Color-coded messages (info, warning, success, decision)
- Auto-scrolling live feed
- Detailed reasoning for each decision

### 🎛️ Interactive Controls

- **Brightness Threshold Slider**: Adjust your preferred light intensity
- Visual feedback with animated sun icon
- Real-time energy savings calculation
- Preference persistence via API

### 📊 Real-time Data

- WebSocket connection for sub-100ms latency updates
- Live sensor readings (LDR, current, temperature, humidity)
- Energy source switching notifications
- Grid carbon intensity monitoring

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **3D Graphics**: React Three Fiber + Three.js
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Icons**: Lucide React
- **Real-time**: WebSocket API

## Installation

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Running HyperVolt backend (Django API)

### Setup

1. Navigate to the website directory:
```bash
cd website
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your backend URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_3D=true
```

4. Run development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
website/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main dashboard page
│   └── globals.css         # Global styles and animations
├── components/
│   ├── DigitalTwin.tsx     # 3D room visualization
│   ├── EnergyFlow.tsx      # Energy flow diagram
│   ├── EnergyChart.tsx     # Forecast charts
│   ├── StatsGrid.tsx       # Statistics cards
│   ├── BrightnessControl.tsx # Brightness slider
│   └── StrategyNarrator.tsx  # Live log viewer
├── hooks/
│   └── useWebSocket.ts     # WebSocket connection hook
├── lib/
│   ├── api-service.ts      # API client
│   ├── types.ts            # TypeScript interfaces
│   └── utils.ts            # Utility functions
├── .env.local              # Environment variables
├── package.json            # Dependencies
└── README.md              # This file
```

## API Integration

The website connects to the Django backend via REST API and WebSockets.

### REST API Endpoints

- `GET /api/ai/status/` - Check AI models availability
- `GET /api/ai/forecast/?hours=6` - Get energy forecast
- `GET /api/energy-sources/` - Get available energy sources
- `GET /api/sensor-readings/` - Get sensor data
- `GET /api/grid-data/carbon_intensity/` - Get carbon intensity
- `PATCH /api/preferences/{key}/` - Update user preferences

### WebSocket

Connect to `ws://localhost:8000/ws/sensors/` for real-time updates:
- Sensor readings (LDR, current, temperature)
- Energy source switching events
- AI decisions and recommendations

## Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Django backend URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket server URL | `ws://localhost:8000` |
| `NEXT_PUBLIC_ENABLE_3D` | Enable 3D visualization | `true` |

## Troubleshooting

### WebSocket Connection Failed
- Ensure Django backend is running
- Check CORS settings in Django
- Verify WebSocket URL in `.env.local`

### 3D Scene Not Rendering
- Check browser WebGL support
- Update graphics drivers
- Disable browser extensions

### API Calls Failing
- Verify backend is running on correct port
- Check API URL in `.env.local`
- Ensure Django CORS headers are configured

## License

MIT License - Part of HyperVolt project

## Team

Built with ❤️ by HyperHawks Team for SMVIT Sustainergy Hackathon 2026

---

**Status**: ✅ Complete & Production Ready  
**Last Updated**: January 26, 2026  
**Version**: 1.0.0
