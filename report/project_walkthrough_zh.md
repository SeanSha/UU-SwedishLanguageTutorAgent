# 项目大白话说明：这个 Swedish Tutor Agent 到底在做什么

这份文档是给你自己理解项目用的。你录视频或回答老师问题时，可以按这个逻辑讲。

## 1. 一句话解释

这个项目不是一个普通聊天机器人，而是一个 **AI Swedish Tutor Agent**。用户先选一个生活场景，比如买东西、交通、学校、看病。系统会先去自己的瑞典语学习数据里检索这个场景相关的：

- 对话计划
- 单词
- 例句

然后再把这些检索结果整理成练习页面，让用户听瑞典语、看翻译、做小测验、最后把错过的词放进 memory 里复习。

## 2. 为什么它算 Agent

它不是只把用户输入丢给 LLM。它有几个工具，每一步会调用不同工具完成任务：

- `structured_retrieval_tool.py`：根据 topic 找对话计划、单词、例句。
- `dialogue_tool.py`：控制当前在第几轮对话，避免对话乱跳。
- `quiz_tool.py`：根据当前句子生成选择题或填空题。
- `feedback_tool.py`：判断答案对不对。
- `memory_tool.py`：记录用户哪些词容易错。
- `tts_avatar_tool.py`：生成或播放瑞典语音频。
- `online_client.py` / `ollama_client.py`：连接在线模型或本地模型。

所以它是一个有状态、有工具、有记忆、有行动的学习 Agent。

## 3. 信息检索 IR 在哪里

IR 的核心在于：用户不是直接问 LLM “帮我编一个瑞典语对话”。系统会先从数据集中检索适合当前 topic 的材料。

比如用户选择 Food Shop：

1. 系统找到 food shop 的 dialogue plan。
2. 找到这个场景的 vocabulary，比如 `äpple`, `mjölk`, `kostar`。
3. 找到相关例句，比如 `Vad kostar det?`。
4. 把这些结果显示在 Lesson Study Guide 里。
5. 再用这些内容生成练习流程。

这样做的好处是：LLM 不会随便发散，练习内容会稳定地围绕数据集和学习目标。

## 4. Memory 是怎么工作的

Memory 不是为了炫技，而是为了让学习有连续性。

用户答错一个词，比如 `skolan`，系统会把它记录到 memory 里，并给它一个 review weight。答错越多，权重越高。以后系统会：

- 在 Memory Review Coach 里显示它。
- 在 Memory Review Quiz 里让用户重新练。
- 在之后的题目里更容易再次遇到它。

答对以后，这个词的权重会下降。下降到 0 就代表暂时掌握了。

这就是一个很简单的 spaced repetition 思路。

## 5. Memory Review Quiz 为什么重要

原来 memory 只是显示“你错了哪些词”，这不太像功能。现在它变成一个可互动的复习页面：

1. 点击 `Start Memory Review Quiz`。
2. 系统从 memory 里挑最需要复习的词。
3. 一张卡片显示一个瑞典语词。
4. 用户可以点按钮听发音。
5. 用户选择英文意思。
6. 答对就降低 memory 权重，答错就提高权重。

这样 memory 就形成闭环：记录错误 -> 生成复习 -> 更新记忆状态。

## 6. Online Mode 应该怎么解释

项目支持两种模式：

- Local Mode：用 Ollama 本地模型。
- Online Mode：用 OpenAI-compatible API。

默认配置是 OpenAI：

```text
Base URL: https://api.openai.com/v1
Model: gpt-4o-mini
```

如果课程用 Berget，也可以在 UI 里改成：

```text
Base URL: https://api.berget.ai/v1
Model: openai/gpt-oss-120b
```

重点是：代码不绑定某一个平台，只要是 OpenAI-compatible chat completion 格式，就可以运行。

## 7. 录视频时怎么讲

你可以按这个顺序录：

1. 打开 GitHub README，说明项目目标。
2. 启动 `python app.py`。
3. 展示 Online Mode 可以填 API key/base/model。
4. 选择一个 topic，例如 Food Shop。
5. 展示 Lesson Study Guide：
   - Vocabulary
   - Retrieved Sentence Examples
   - Example Dialogue
6. 开始一轮对话，听瑞典语音频，做选择题。
7. 故意选错一个词，展示 feedback 和 memory 更新。
8. 打开 Memory Review Quiz，复习错词。
9. 说明这个系统以后可以扩展：
   - 更多数据
   - 更强 retrieval
   - 文档搜索
   - 更长期的 memory

## 8. 你可以对老师说的核心贡献

这个项目的核心贡献不是 UI 好看，而是：

> I built a Swedish learning agent where the dialogue is grounded in retrieved topic-specific teaching material, and the agent uses memory to adapt later retrieval and review actions.

中文理解就是：

> 我做的是一个用检索结果控制对话内容的瑞典语学习 Agent，并且它会记住用户薄弱词汇，再主动生成复习任务。
