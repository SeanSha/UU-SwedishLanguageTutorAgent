# Code Walkthrough For Newcomers

This document explains how the project code is organised and how one full practice session flows through the system. It is written for someone who is new to the repository and wants to understand the code before modifying it.

## 1. What This Project Is

This project is a Swedish language learning agent. The user chooses a topic, such as food shopping or transport. The system retrieves relevant teaching material from local data files, builds a guided lesson, asks quiz questions, records mistakes, and creates follow-up memory review cards.

The important design idea is:

```text
Topic choice -> retrieve context -> build dialogue practice -> quiz user -> update memory -> review weak words
```

The project is not just a chatbot. It is an agent because it uses tools, state, memory, and actions.

## 2. Main Entry Point

The app starts from:

```text
app.py
```

At the bottom of `app.py`, Gradio launches the web app:

```python
if __name__ == "__main__":
    demo.launch(...)
```

When you run:

```bash
python app.py
```

Gradio starts a local web page, usually at:

```text
http://127.0.0.1:7860
```

## 3. Most Important Files

```text
app.py
```

Builds the user interface. It contains the setup screen, lesson screen, Memory Review Coach, and Memory Review Quiz page. It also wires button clicks to Python functions.

```text
agent.py
```

Contains the main `SwedishSpeakingAgent`. This class coordinates retrieval, dialogue state, quiz generation, feedback, TTS, and memory.

```text
config.py
```

Stores paths and default model settings. API keys are read from environment variables and are not stored in git.

```text
data_loader.py
```

Loads structured local data from JSONL files.

```text
tools/
```

Contains the agent's tools. Each tool has a focused job, such as retrieval, quiz generation, memory, or TTS.

```text
llm/
```

Contains local and online LLM clients.

```text
data/
```

Contains the teaching dataset: dialogue plans, vocabulary, and sentence examples.

## 4. Data Files

The project uses three main structured data files:

```text
data/dialogue_plans.jsonl
```

Stores scenario-level dialogue plans. A plan says what should happen turn by turn.

```text
data/vocabulary.jsonl
```

Stores Swedish words, English meaning, Chinese meaning, part of speech, and example sentence.

```text
data/sentence_examples.jsonl
```

Stores example Swedish sentences for different scenario functions, such as greeting, asking location, buying something, or giving an answer.

These files are important because the agent should not invent the whole lesson randomly. It should ground its output in retrieved teaching material.

## 5. Tool Modules

### `tools/structured_retrieval_tool.py`

This is the main retrieval tool. When the user selects a topic, it retrieves:

- one dialogue plan
- vocabulary for the topic
- sentence examples
- turn-by-turn examples for the plan

This is the main IR component used by the final lesson flow.

### `tools/retrieval_tool.py`

This is the older retrieval tool. It supports semantic or TF-IDF retrieval and includes memory boosting. It is still useful as a demonstration of memory-aware IR scoring.

### `tools/dialogue_tool.py`

Controls which dialogue turn the learner is currently on. This prevents the UI from losing track of the conversation.

### `tools/quiz_tool.py`

Generates quiz questions. It can create:

- multiple-choice questions
- fill-in-the-blank questions

It now prefers words that can be explained by the vocabulary resolver, so the app avoids showing unclear meanings like "vocabulary word".

### `tools/feedback_tool.py`

Checks the user's answer. If the answer is wrong, it records the mistake in memory. If the answer is right, it records success.

### `tools/memory_tool.py`

Stores learner memory in local JSON. The runtime memory file is ignored by git:

```text
memory/user_memory.json
```

The memory stores difficult words and counts correct/incorrect answers.

### `tools/tts_avatar_tool.py`

Handles Swedish text-to-speech and avatar images. It caches generated MP3 files locally. Empty MP3 files are treated as invalid and removed.

### `tools/vocab_resolver.py`

Resolves Swedish word forms into learner-friendly meanings. For example:

```text
skolan -> skola -> school / 学校
bussen -> buss -> bus / 公交车
huvudet -> huvud -> head / 头
```

This module is important because quiz words often appear in inflected Swedish forms.

## 6. LLM Modules

### `llm/llm_provider.py`

Routes requests to either local mode or online mode.

### `llm/ollama_client.py`

Connects to a local Ollama server.

### `llm/online_client.py`

Connects to an OpenAI-compatible endpoint. By default:

```text
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_ONLINE_MODEL=gpt-4o-mini
```

For Berget AI, the user can change the UI fields or `.env` values.

## 7. One Full Lesson Flow

Here is what happens when the user starts a lesson.

### Step 1: User chooses a scenario

In `app.py`, scenario buttons update a hidden `scenario_select` value.

Example:

```text
Food Shop -> food_shop
Transport -> transport
```

### Step 2: User clicks Start

The button calls:

```python
handle_start_agent(...)
```

This function calls:

```python
agent.start_practice(...)
```

### Step 3: Agent retrieves topic context

Inside `agent.start_practice`, the agent retrieves:

- topic vocabulary
- dialogue plan
- sentence examples
- turn-by-turn examples

The result is stored in:

```python
agent.topic_context
```

### Step 4: UI builds Lesson Study Guide

`app.py` calls:

```python
build_study_guide_html(agent.retrieved_examples_log, agent.topic_context)
```

This creates the top study guide:

1. Vocabulary Warm-up
2. Retrieved Sentence Examples
3. Example Dialogue

Vocabulary and examples are clickable for audio.

### Step 5: Dialogue state starts

The dialogue tool selects the first turn. The UI shows:

- Sven's Swedish sentence
- translation
- audio
- expected learner quiz

### Step 6: Quiz is generated

The quiz tool blanks out a Swedish word or creates multiple-choice options.

Example:

```text
Jag vill ha ett ____.
```

Options might be:

```text
äpple, mjölk, skola, buss
```

### Step 7: User answers

Answer buttons call:

```python
handle_submit_answer(...)
```

This function sends the answer to the feedback tool.

### Step 8: Memory updates

If the answer is wrong:

```text
wrong word score +2
```

If the answer is correct:

```text
wrong word score -1
```

This is how the memory system creates a simple spaced repetition effect.

### Step 9: User continues

The `Continue` button calls:

```python
handle_load_next_turn(...)
```

The next dialogue turn is loaded until the scenario is complete.

## 8. Memory Review Flow

The Memory Review Coach is shown below the lesson. It summarises:

- total practice answers
- correct memory count
- review queue size
- words to review next

When the user clicks:

```text
Start Memory Review Quiz
```

`app.py` calls:

```python
handle_open_memory_review()
```

This builds review cards from memory:

```python
build_memory_review_items()
```

Each review card asks the user to choose the meaning of a weak Swedish word. Correct answers reduce the review score. Wrong answers increase it.

## 9. Online Mode Flow

Online mode is configured in the advanced settings panel.

The user provides:

```text
API key
API base URL
Model name
```

For OpenAI:

```text
https://api.openai.com/v1
gpt-4o-mini
```

For Berget:

```text
https://api.berget.ai/v1
openai/gpt-oss-120b
```

The online client is in:

```text
llm/online_client.py
```

The app currently defaults to stable retrieval-grounded dialogue. If the environment variable below is set, online LLM dialogue generation can be enabled:

```bash
USE_LLM_DIALOGUE_GENERATION=1 python app.py
```

For the assignment demo, the default stable mode is usually better because the dialogue is easier to reproduce.

## 10. What To Modify If You Extend The Project

### Add a new topic

Update:

- `data/dialogue_plans.jsonl`
- `data/vocabulary.jsonl`
- `data/sentence_examples.jsonl`
- `config.py` scenario list
- `SCENARIO_MAP` in `app.py`

### Improve retrieval

Start with:

```text
tools/structured_retrieval_tool.py
```

Possible improvements:

- add embeddings
- add reranking
- add document search
- add grammar-note retrieval

### Improve memory

Start with:

```text
tools/memory_tool.py
```

Possible improvements:

- store timestamps
- add spaced repetition scheduling
- track grammar mistakes separately
- save per-user profiles

### Improve quiz logic

Start with:

```text
tools/quiz_tool.py
tools/vocab_resolver.py
```

The quiz tool chooses target words. The vocabulary resolver explains them.

## 11. Common Problems

### Online mode says API key invalid

Check:

- API key is pasted correctly
- base URL matches the provider
- model name exists on the provider

### Audio does not play

The app first tries cached MP3 audio. If MP3 generation fails, it falls back to browser speech synthesis. Empty MP3 cache files are automatically removed.

### Memory review shows no cards

That means there are no active wrong words. Answer some lesson questions incorrectly, then open Memory Review Quiz again.

### The app cannot load SentenceTransformers

The app has a fallback retrieval mode, so this should not stop the project from running.

## 12. Mental Model

The easiest way to understand the project is:

```text
app.py is the screen.
agent.py is the coordinator.
tools/ are the agent's actions.
data/ is the teaching knowledge.
memory/ is the learner history.
llm/ is the model connection.
```

If something appears wrong in the UI, start from `app.py`.
If the dialogue logic is wrong, check `agent.py` and `dialogue_tool.py`.
If retrieved examples are wrong, check `structured_retrieval_tool.py`.
If quiz words or meanings are wrong, check `quiz_tool.py` and `vocab_resolver.py`.
If memory behaviour is wrong, check `memory_tool.py`.
