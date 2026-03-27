# 🧠 Prompt Engineering Log — Cloudflare AI Chat Assistant

## Overview

This document describes the AI-assisted development process used to build the Cloudflare AI Chat Assistant. It includes the prompts used, the reasoning behind each decision, issues encountered, and how they were resolved.

---

## Prompt 1 — Initial Scaffolding

### Prompt
> I want to build a simple AI chat for a Cloudflare internship assignment. I need the app to use Python Workers, Workers AI (Llama 3.3) for the responses, and Workers KV to remember what the user said before. Provide a basic `entry.py` and the `wrangler.jsonc` file to get this started.

### Why this prompt
I started broad to get a working scaffold quickly. By specifying the exact stack (Python Workers, Workers AI with Llama 3.3, Workers KV), I avoided generic responses and got output immediately relevant to the Cloudflare ecosystem.

### Outcome
Got a working base structure. The frontend was served correctly and KV reads/writes functioned as expected.

---

## Prompt 2 — Debugging AI Binding Error

### Prompt
> I tried running the code you gave me, but I'm getting an error when the Python backend tries to talk to the AI service. It seems like the data format between Python and Cloudflare's internal system isn't matching. Can you fix the code to ensure the AI binding receives the messages correctly?

### Why this prompt
After running the initial scaffold, the Workers AI binding was throwing a serialization error. I described the symptom rather than guessing the fix, which led to a more accurate solution.

### What was fixed
Messages were being passed as a raw Python `list` — the fix involved explicitly converting the payload using `js.JSON.parse(json.dumps(...))` to bridge the Python/JS boundary correctly.

### Outcome
AI responses started flowing correctly after the serialization fix.

---

## Prompt 3 — Adding New Features

### Prompt
> I want to extend the Cloudflare AI Chat Assistant with three new features:
> 1. A "Clear History" button that deletes the KV session and resets the chat
> 2. A persistent session indicator that shows the user their history was loaded
> 3. A customizable system prompt input so the user can change the assistant's behavior
> Keep everything in a single entry.py file using Python Workers.

### Why this prompt
The base version was functional but felt too minimal as a product. I grouped all three features into a single prompt to avoid multiple round-trips and to ensure the AI reasoned about how the features would interact with each other.
