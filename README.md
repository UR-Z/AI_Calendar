# Strands Agent: Multi-Agent Orchestrator & Multimodal Calendar App

## Overview

This repository demonstrates a system using [Strands Agents](https://strandsagents.com/latest/), featuring:

- **Multi-Agent Orchestrator**: Routes user queries to specialist agents for math, programming, language, research, and general knowledge tasks.
- **Multimodal Calendar App**: A Streamlit-based app that manages calendar events via text and image (e.g., extracting events from a photo of a fridge calendar).

## Project Structure

```
Strands Agent/
├── __init__.py
├── bedrock_model.py         # Model provider configuration (uses environment variables)
├── calendar_app.py          # Streamlit app for calendar management
├── calendar_prompt.txt      # Prompt for calendar event extraction
├── tools.py                 # Specialist agent tools
├── requirements.txt         # Python dependencies
├── README.md                # This file
```

## Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials** (for Bedrock model):
   - Set environment variables in a `.env` file or your shell:
     ```env
     AWS_ACCESS_KEY_ID=your_key
     AWS_SECRET_ACCESS_KEY=your_secret
     ```

3. **Run the calendar app:**
   ```bash
   streamlit run calendar_app.py
   ```

## Security & Sensitive Information

- **No API keys or secrets are stored in this repository.**
- All credentials are loaded from environment variables (see `.env.example`).
- Do not commit your `.env` or any files containing secrets.

## Customization

- Add new specialist agents in `tools.py`.
- Update model provider in `bedrock_model.py` as needed.

## License

MIT License. See [LICENSE](LICENSE) for details. 
