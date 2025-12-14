# Fight or Delight

A voice-powered sentiment analyzer that helps you understand how your day went!

## Features

- **Voice Recording**: Uses the Web Speech API to capture and transcribe your voice in real-time
- **VADER-style Sentiment Analysis**: Analyzes your transcript using a sophisticated algorithm that considers:
  - Positive and negative word detection with weighted scores
  - Intensifiers (very, extremely, absolutely, etc.)
  - Negation handling (not good, never happy, etc.)
- **Beautiful UI**: Modern gradient design with smooth animations
- **Instant Results**: See whether your day was a "Fight" (negative) or a "Delight" (positive)

## Tech Stack

- React 18
- Tailwind CSS (via CDN)
- Lucide React icons
- Web Speech API

## Getting Started

1. Start a local server:
   ```bash
   python3 -m http.server 8080
   ```

2. Open your browser to `http://localhost:8080`

3. Click the microphone button and start talking about your day

4. Click "Analyze My Day" to see your results!

## Browser Support

The Web Speech API is supported in:
- Google Chrome
- Microsoft Edge
- Safari

## How It Works

The sentiment analyzer uses a VADER-style approach:

1. **Word Scoring**: Each word is checked against positive and negative word lists with pre-assigned sentiment scores
2. **Intensifier Boosting**: Words like "very" or "extremely" amplify the sentiment of nearby words
3. **Negation Handling**: Negation words flip the sentiment of following words (e.g., "not happy" becomes negative)
4. **Score Normalization**: The raw score is normalized to a -1 to +1 range for consistent results
