# Technology Stack

## Frontend
- **Framework**: Next.js 15.4.6
- **UI Library**: React 19.1.0
- **Styling**: Tailwind CSS v4
- **State Management**: Zustand 5.0.7
- **WebSocket Client**: react-use-websocket 4.13.0
- **Icons**: lucide-react
- **Language**: TypeScript 5

## Backend
- **Framework**: FastAPI 0.115.4
- **Server**: Uvicorn 0.32.0
- **WebSocket**: websockets 13.1
- **Async HTTP**: aiohttp 3.10.10, httpx 0.27.0
- **Data Validation**: Pydantic 2.9.2
- **Configuration**: PyYAML 6.0.2, python-dotenv 1.0.1

## LLM APIs
- **OpenAI**: openai 1.54.3
- **Anthropic**: anthropic 0.39.0
- **Google Gemini**: google-generativeai 0.8.3
- **xAI Grok**: xai-sdk 0.1.0

## Key Changes from OpenArena
- Replaced Ollama with cloud APIs (OpenAI, Anthropic, Google, xAI)
- Changed from 3-column layout to 2ch-style vertical scroll
- Added LocalStorage persistence (was memory-only)