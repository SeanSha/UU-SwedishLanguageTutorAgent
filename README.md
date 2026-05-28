# UU Swedish Language Tutor Agent

A Gradio-based AI agent for beginner Swedish practice. The learner selects a real-life topic, the agent retrieves structured dialogue plans, vocabulary, and sentence examples, then turns that retrieved context into a guided listening, reading, quiz, and memory-review workflow.

This project was built for **Assignment 2: AI Agents** in 5LN712. It focuses on how an agent can use **Information Retrieval (IR)**, memory, and tool actions to keep a language-learning dialogue grounded and extensible.

## Demo

Video link: add the recorded video link here before submission.

## Main Features

- **OpenAI-compatible Online Mode**: runs with an OpenAI-format API key through the UI or `.env`.
- **Local Mode**: optional Ollama support for local models.
- **Structured IR**: retrieves topic-specific dialogue plans, vocabulary, and sentence examples from local JSONL cache files.
- **Memory-aware retrieval**: records difficult words and boosts them in later retrieval/quiz contexts.
- **Interactive Swedish practice**: each lesson has vocabulary, retrieved examples, generated dialogue turns, translations, quiz questions, and TTS.
- **Memory Review Quiz**: converts remembered weak vocabulary into clickable review flashcards.
- **Extensible tool design**: retrieval, quiz generation, feedback, TTS, memory, and LLM providers are separated into tool/client modules.

## Quick Start

```bash
git clone https://github.com/SeanSha/UU-SwedishLanguageTutorAgent.git
cd UU-SwedishLanguageTutorAgent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the Gradio URL printed in the terminal, usually:

```text
http://127.0.0.1:7860
```

## Online Mode Setup

The assignment asks for runnable code given an API key in OpenAI format. You can either paste the key directly into the UI or create a local `.env` file:

```bash
cp .env.example .env
```

Default OpenAI-compatible settings:

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_ONLINE_MODEL=gpt-4o-mini
```

For Berget AI, use the same UI fields with an OpenAI-compatible base URL, for example:

```env
OPENAI_API_BASE=https://api.berget.ai/v1
DEFAULT_ONLINE_MODEL=openai/gpt-oss-120b
```

No API key is committed to this repository.

## Local Mode Setup

Local mode uses Ollama:

```bash
ollama pull qwen2.5
ollama serve
python app.py
```

Then keep `Local Mode` selected in the UI.

## How The Agent Works

1. **Topic selection**: the learner chooses a scenario such as food shop, family/school, health, transport, home, or introductions.
2. **IR context retrieval**: `StructuredRetrievalTool` retrieves a dialogue plan, vocabulary list, sentence bank, and turn-by-turn examples.
3. **Prompt/context preparation**: the retrieved context is formatted into a clear teaching context for the dialogue generator.
4. **Practice loop**: the UI shows Swedish narration, translation, the expected learner reply, and a quiz.
5. **Memory update**: wrong answers increase a word's review weight; correct answers decay it.
6. **Memory review**: weak words become review flashcards with audio, meanings, and multiple-choice reinforcement.

## Architecture

```text
app.py
  Gradio UI, lesson screens, memory review page

agent.py
  Main SwedishSpeakingAgent orchestration

tools/
  structured_retrieval_tool.py  topic IR over plans/vocabulary/examples
  retrieval_tool.py             legacy semantic/TF-IDF retrieval with memory boost
  quiz_tool.py                  multiple-choice and fill-in-the-blank quizzes
  feedback_tool.py              answer checking and memory updates
  memory_tool.py                local JSON memory store
  tts_avatar_tool.py            Swedish TTS cache and avatar assets
  vocab_resolver.py             Swedish word-form meaning resolver

llm/
  llm_provider.py               local/online router
  online_client.py              OpenAI-compatible client
  ollama_client.py              local Ollama client

data/
  dialogue_plans.jsonl
  vocabulary.jsonl
  sentence_examples.jsonl
```

## IR And Memory Design

The project uses two complementary retrieval layers:

- **Structured retrieval** selects the relevant topic plan, vocabulary, and example sentences.
- **Memory-aware retrieval** stores difficult words and gives matching examples a higher priority in later practice.

This keeps the system grounded in the dataset while still adapting to the learner. The memory is intentionally local and simple (`memory/user_memory.json`, ignored by git), so the project can be extended later with document search, update actions, or more advanced memory stores.

## Running A Test

```bash
python -m py_compile app.py agent.py tools/*.py llm/*.py
python test_planner.py
```

Then run the UI and test:

1. Start a lesson.
2. Answer one or two quiz turns.
3. Check that Memory Review Coach updates.
4. Open Memory Review Quiz.
5. Try Online Mode with an OpenAI-compatible key.

## Notes For Submission

Include in the final Canvas submission:

- GitHub repository link: `https://github.com/SeanSha/UU-SwedishLanguageTutorAgent`
- Video link: add after recording
- Report: see `report/assignment2_report.md`
- Personal project explanation: see `report/project_walkthrough_zh.md`
