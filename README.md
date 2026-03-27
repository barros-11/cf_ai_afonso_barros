# 🤖 Cloudflare AI Chat Assistant (Python Worker)
Note: This project was developed 100% using AI assistance as a collaborative architect. The primary goal was to build a functional, end-to-end MVP in just a few hours, focusing on simplicity and the practical integration of Cloudflare's newest features.
A simple AI-powered chat application built for the Cloudflare Software Engineering Internship assignment. This project demonstrates a complete serverless flow using the Cloudflare Workers Python environment.

## 🚀 What it does
- **Frontend:** A minimalist web interface served directly from a Python Worker.
- **Workflow:** Processes user messages, maintains session state, and fetches AI responses.
- **AI Engine:** Uses `Llama 3.3` on Workers AI for natural language interaction.
- **Memory:** Integrated with Cloudflare KV to store and retrieve chat history (contextual awareness).

## 🛠️ Technical Stack
- **Backend:** Cloudflare Workers (Python / Pyodide)
- **AI Model:** `@cf/meta/llama-3.3-70b-instruct-fp8-fast`
- **Database:** Workers KV (`CHAT_HISTORY`)

## 🔗 Live Demo
[**View Live Project**](https://cf-ai-assistant.afonsocapabarroz.workers.dev)

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/afonsocapabarroz/cf_ai_assistant
   cd cf_ai_assistant
   ```

2. **Login to Cloudflare:**
   ```bash
   npx wrangler login
   ```

3. **Setup KV Namespace:**
   Create the required KV namespace for chat memory:
   ```bash
   npx wrangler kv:namespace create "CHAT_HISTORY"
   ```
   > **Note:** Ensure the generated id is updated in your `wrangler.jsonc` file.

4. **Run locally:**
   ```bash
   npx wrangler dev
   ```

5. **Deploy to production:**
   ```bash
   npx wrangler deploy
   ```