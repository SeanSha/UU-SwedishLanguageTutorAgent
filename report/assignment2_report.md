# Assignment 2 Report: Swedish Language Tutor Agent

**Project:** UU Swedish Language Tutor Agent  
**GitHub:** https://github.com/SeanSha/UU-SwedishLanguageTutorAgent  
**Video:** add video link before submission  

## 1. Project Goal

The goal of this project is to build an AI agent that helps beginner learners practise Swedish in controlled everyday scenarios. Instead of using a general chatbot that may generate random or too difficult language, the system grounds each lesson in retrieved teaching material: dialogue plans, vocabulary, and sentence examples. The learner selects a topic, such as food shopping or transport, and the agent retrieves relevant context before generating a structured practice dialogue.

The project is designed around the assignment theme of AI agents and Information Retrieval. The agent performs tool actions for retrieval, memory lookup, quiz generation, answer checking, and text-to-speech. These tools are separated into modules so that the system can be extended later with stronger IR methods or new actions.

## 2. System Design

The application is implemented as a Python Gradio web app. The main interface contains a setup screen, a lesson practice screen, and a memory review quiz. The central class is `SwedishSpeakingAgent` in `agent.py`, which coordinates the tool calls and keeps the dialogue state.

The learning flow is:

1. The user selects a topic label.
2. The structured retrieval tool retrieves a topic-specific dialogue plan, vocabulary list, and sentence examples from local JSONL data.
3. The agent formats the retrieved material as lesson context.
4. The dialogue tool creates a stable turn-by-turn practice flow.
5. The quiz tool generates multiple-choice or fill-in-the-blank exercises.
6. The feedback and memory tools update the learner model after each answer.
7. The TTS tool provides Swedish audio for dialogue sentences and review cards.

The overall architecture is shown below as a layered system. The design separates the user interface, agent orchestration, tools, knowledge sources, memory, and model connection. This makes the system easier to extend with new retrieval tools or new agent actions.

```mermaid
flowchart LR
    subgraph L1["User Layer"]
        User["Learner<br/>chooses topic<br/>answers quiz<br/>reviews weak words"]
    end

    subgraph L2["Interface Layer"]
        UI["Gradio UI<br/>app.py"]
        Guide["Lesson Study Guide<br/>vocabulary + examples + dialogue"]
        ReviewUI["Memory Review Quiz<br/>flashcard practice"]
    end

    subgraph L3["Agent Orchestration Layer"]
        Agent["SwedishSpeakingAgent<br/>agent.py"]
        State["Dialogue State<br/>current turn, history, active quiz"]
    end

    subgraph L4["Tool Layer"]
        Retrieval["Structured Retrieval Tool<br/>topic context retrieval"]
        Dialogue["Dialogue Tool<br/>turn control"]
        Quiz["Quiz Tool<br/>exercise generation"]
        Feedback["Feedback Tool<br/>answer checking"]
        TTS["TTS + Avatar Tool<br/>audio and tutor state"]
        VocabResolver["Vocabulary Resolver<br/>Swedish word forms to meaning"]
    end

    subgraph L5["Knowledge and Memory Layer"]
        Dataset["Hugging Face / Local JSONL Data<br/>plans, vocabulary, examples"]
        Memory["Learner Memory<br/>wrong words + review weights"]
    end

    subgraph L6["Model Layer"]
        Provider["LLM Provider<br/>model router"]
        Online["OpenAI-compatible API"]
        Local["Ollama Local Model"]
    end

    User --> UI
    UI --> Agent
    Agent --> State
    Agent --> Retrieval
    Agent --> Dialogue
    Agent --> Quiz
    Agent --> Feedback
    Agent --> TTS
    Quiz --> VocabResolver
    Feedback --> Memory
    Retrieval --> Dataset
    Memory -.boosts future retrieval.-> Retrieval
    Memory -.creates review cards.-> ReviewUI
    Agent --> Provider
    Provider --> Online
    Provider --> Local
    Retrieval --> Guide
    Guide --> UI
    TTS --> UI
    ReviewUI --> UI
```

The runtime flow for one lesson is:

```mermaid
sequenceDiagram
    participant U as Learner
    participant UI as Gradio UI
    participant A as SwedishSpeakingAgent
    participant IR as Retrieval Tool
    participant D as Local Dataset
    participant Q as Quiz + Feedback Tools
    participant M as Memory Tool
    participant T as TTS Tool

    U->>UI: Select topic and start lesson
    UI->>A: start_practice(topic, quiz_type, language)
    A->>IR: retrieve dialogue plan, vocabulary, examples
    IR->>D: read plans, vocabulary, sentence examples
    D-->>IR: topic-specific teaching context
    IR-->>A: structured retrieval bundle
    A-->>UI: lesson guide + first dialogue turn
    UI-->>U: show vocabulary, examples, Swedish sentence, quiz
    U->>UI: answer quiz
    UI->>Q: check answer
    Q->>M: update wrong/correct word memory
    Q-->>UI: feedback and correction
    UI-->>U: show feedback and next-turn controls
    U->>UI: open Memory Review Quiz
    UI->>M: get weak words
    M-->>UI: review queue
    UI->>T: play/recover Swedish audio
    UI-->>U: flashcard review practice
```

Online mode uses an OpenAI-compatible chat completion client. The code can run with an OpenAI API key through the UI or through `.env` settings. It can also use compatible endpoints such as Berget AI by changing the base URL and model name.

## 3. Information Retrieval Component

The core IR component is the structured retrieval pipeline. The project uses local cached data files:

- `data/dialogue_plans.jsonl`
- `data/vocabulary.jsonl`
- `data/sentence_examples.jsonl`

These local files are based on my Hugging Face dataset:

`SeanSha30/swedish-pre-a1-learning-agent-dataset`  
https://huggingface.co/datasets/SeanSha30/swedish-pre-a1-learning-agent-dataset

For each selected topic, the retrieval tool selects the relevant plan and ranks sentence examples by topic, function, slots, and keyword overlap. This retrieved context is shown in the UI as a lesson guide: first vocabulary, then retrieved sentence examples, then an example dialogue. This makes the retrieval visible to the learner and to the evaluator.

The project also includes a memory-aware retrieval layer. The memory tool stores words the learner got wrong, together with a review weight. Later retrieval and quiz generation can reuse those difficult words, making the system adaptive rather than stateless.

## 4. Memory And Agent Actions

The agent has a simple local memory stored in `memory/user_memory.json` at runtime. This file is ignored by git so personal progress is not uploaded. When a learner answers incorrectly, the relevant word receives a higher review weight. When the learner answers correctly, the weight decays.

This memory is used in two ways:

- It affects practice by prioritising difficult words in retrieval and quiz distractors.
- It powers a separate Memory Review Quiz where the learner reviews weak vocabulary as flashcards.

The memory review page is an important agent action because it turns remembered information into a new task. The agent is not only displaying statistics; it actively creates follow-up practice based on previous learner behaviour.

## 5. Extensibility

The system is intentionally modular. Retrieval, quiz generation, feedback, TTS, memory, and LLM calls are separate tools. This makes the project extendable in several directions:

- Replace keyword ranking with vector search or a database index.
- Add document search for course material or grammar notes.
- Add update actions, such as writing new vocabulary into a learner profile.
- Replace local JSON memory with a more advanced long-term memory store.
- Add more languages or more detailed CEFR-level progression.

This satisfies the requirement that the system should be extendable with IR tools and/or action tools.

## 6. Reflection On AI-Assisted Development

AI coding tools were useful for building and debugging the project, especially when connecting multiple modules and improving the user interface. However, the main challenge was not simply generating code. The difficult part was controlling the dialogue state, making the retrieval results actually influence the lesson, and preventing the UI from becoming confusing.

Through iteration, the system became simpler and more reliable. The final design avoids unnecessary randomness by grounding the lesson in retrieved data. This made the project more suitable as a student assignment: it demonstrates agent architecture, memory, and IR clearly without pretending to be a full commercial product.

The main lesson from using AI tools is that they are powerful for implementation, but the developer still needs to inspect, test, and simplify the design. In this project, AI assistance helped accelerate development, while manual testing and design decisions were necessary to make the agent understandable and stable.

## 7. Submission Checklist

- GitHub repository: https://github.com/SeanSha/UU-SwedishLanguageTutorAgent
- Runnable with OpenAI-compatible API key
- Modular IR and tool-based agent design
- Memory and review action implemented
- Video demonstration: add link before submission
