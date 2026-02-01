Perfect. Then we **lock this as a core architectural requirement**.

Below is an **updated, final requirements section** focused specifically on **pluggable AI providers (OpenAI, Claude, Gemini)**, while keeping everything **non-commercial, YouTube-first, pygame + Python**.

---

# Among Us — AI Bots Experiment

**Requirements Document (LLM-Pluggable Edition)**

## 1. Project Intent (Final)

* A **non-commercial AI experiment**
* Built **only for fun, learning, and YouTube content**
* Faithful to **Among Us gameplay**
* Entirely **AI-controlled**
* Built using **Python + pygame**
* Designed so **different LLM APIs can be swapped in and compared**

This project should let you answer questions like:

* “How does GPT play compared to Claude?”
* “Which model lies better?”
* “Which model accuses innocents more often?”

---

## 2. Core Architectural Principle

> **The game engine must never depend on a specific AI provider.**

LLMs are **plugins**, not dependencies.

---

## 3. Supported AI Providers (Pluggable)

The system must support:

* OpenAI (GPT models)
* Anthropic Claude
* Google Gemini
* Local / mock bots (rule-based or random)

All of them must conform to **one common interface**.

---

## 4. AI Provider Abstraction (Critical Requirement)

### Unified AI Interface

Every AI provider must implement this interface:

```python
class AIProvider:
    def decide(self, observation: dict) -> dict:
        """
        Input: limited observation of game state
        Output: structured action decision
        """
```

The **game engine only talks to this interface**, never directly to APIs.

---

## 5. Observation Contract (What AI Receives)

Each AI bot receives **only what a real player would know**.

Example:

```json
{
  "self": {
    "id": 4,
    "role": "impostor",
    "alive": true
  },
  "location": "Electrical",
  "visible_players": [2, 7],
  "recent_events": ["Body found in MedBay"],
  "chat_history": [
    "Player 3: I was in Storage",
    "Player 7: Player 4 looks suspicious"
  ],
  "phase": "discussion"
}
```

❌ No global state
❌ No hidden roles
❌ No map-wide visibility

---

## 6. Action Contract (What AI Can Do)

AI must respond in **strict JSON**.

Examples:

### Movement

```json
{
  "action": "move",
  "direction": "left"
}
```

### Kill (impostor only)

```json
{
  "action": "kill",
  "target_id": 6
}
```

### Discussion

```json
{
  "action": "speak",
  "message": "I saw Player 6 near Electrical earlier."
}
```

### Voting

```json
{
  "action": "vote",
  "target_id": 6
}
```

The **engine validates everything**.

---

## 7. Provider-Specific Implementations

### OpenAI Adapter

```python
class OpenAIProvider(AIProvider):
    ...
```

### Claude Adapter

```python
class ClaudeProvider(AIProvider):
    ...
```

### Gemini Adapter

```python
class GeminiProvider(AIProvider):
    ...
```

### Rule-Based Bot (for testing)

```python
class RuleBot(AIProvider):
    ...
```

This allows:

* Mixed-provider games
* A/B testing in videos
* Easy expansion later

---

## 8. AI Memory Handling (Provider-Agnostic)

Memory is managed **outside** the LLM:

* Short-term memory: last N turns
* Long-term memory: summarized beliefs

LLMs receive **summaries**, not raw logs, to:

* Reduce cost
* Improve consistency
* Keep behavior readable for viewers

---

## 9. Timing & Performance Rules (Important for YouTube)

* pygame loop: 60 FPS
* AI decision tick: 0.5–1.5 seconds
* AI calls must be:

  * Non-blocking
  * Timeout-safe
  * Fail gracefully (fallback action)

If an API fails:

* Bot defaults to “do nothing / skip / random move”

---

## 10. Configuration (Per Video)

Each run should be configurable via a simple config file:

```yaml
players:
  - id: 1
    provider: openai
    personality: logical
  - id: 2
    provider: claude
    personality: aggressive
  - id: 3
    provider: gemini
    personality: chaotic
```

This is **gold for content creation**.

---

## 11. YouTube Content Advantages (Why This Matters)

This design allows videos like:

* “GPT vs Claude vs Gemini — Who Lies Best?”
* “One Gemini Bot Ruined the Entire Game”
* “Can Rule-Based Bots Beat LLMs?”

You are not locked into one model.

---

## 12. Non-Functional Requirements (Final)

* Deterministic game engine
* Reproducible seeds
* Clear on-screen labels (provider + personality)
* Easy recording
* Easy swapping of AI providers

---

## 13. Scope Lock (No Feature Creep)

✅ AI-only players
✅ pygame visuals
✅ Pluggable LLM APIs

❌ Online play
❌ Monetization
❌ Human controls

---
