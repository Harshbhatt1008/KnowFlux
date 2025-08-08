# KnowFlux

A Python application for automated code review using AI.

## What it does

KnowFlux takes a GitHub repository URL and provides an AI-powered code review using the Groq API. It fetches the repository content and analyzes it to give you feedback on code quality, potential issues, and suggestions for improvement.

## Requirements

- Python 3.8 or higher
- A Groq API key

## Setup

1. Install the required packages:
   ```bash
   pip install groq requests python-dotenv
   ```

2. Create a `.env` file in the project folder and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

3. Make sure you have a `prompts.py` file with your system prompt defined as `system_prompt_reviewer`.

## How to use

Run the application:
```bash
python main.py
```

Enter a GitHub repository URL when prompted, and the application will fetch the code and provide an AI review.

## Files

- `main.py` - Main application file
- `prompts.py` - Contains the AI system prompts
- `.env` - Environment variables (create this yourself)