# FinanceX HuggingGPT Frontend

A simple ChatGPT-style frontend for the Student Finance AI Orchestrator backend.

## Features

- **Simple Chat Interface**: Clean, minimal design with text input and send button
- **Real-time Responses**: Connects to the backend API to get financial advice
- **File Upload**: Basic file upload functionality (placeholder)
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:

   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

### Usage

1. **Start a conversation**: Type your financial question in the text box
2. **Send message**: Click the "Send" button or press Enter
3. **Get response**: The AI will provide personalized financial advice
4. **Upload files**: Use the file upload button to attach documents (optional)

### Example Questions

- "Should I invest my $500 summer internship earnings or save it?"
- "How can I save money as a student?"
- "What's the best way to pay off student loans?"
- "How do I start investing with a small amount?"

## API Integration

The frontend communicates with the backend API at:

- `POST /query` - Send queries and receive responses
- `GET /health` - Check backend status

## Customization

- **Styling**: Modify `src/App.css` for custom styles
- **API Endpoint**: Update the fetch URL in `src/App.tsx` if needed
- **Features**: Add more functionality by extending the React components

## Troubleshooting

- **Backend not responding**: Make sure the Python backend is running on port 8000
- **CORS errors**: Check that the backend allows requests from `http://localhost:5173`
- **Build errors**: Run `npm install` to ensure all dependencies are installed

## Development

- **Tech Stack**: React, TypeScript, CSS
- **Build Tool**: Vite
- **Styling**: Custom CSS (no Tailwind for simplicity)

## License

This project is part of the Student Finance AI Orchestrator system.
