# System Prompt 4: Social Media Clipping & Animated Captions (Stub)

**Project:** Autonomous Video Ingestion, Compliance, Rendering, HITL Publishing  
**Status:** DEFERRED — Phase 2  
**Workspace:** `c:/Users/Nicol/MAS/`

---

## 1. Context

Pipeline for processing creator livestreams: extract viral timestamps, filter for platform compliance, generate Spanish animated captions, and publish across social platforms with human approval.

**Do NOT implement now.** This prompt preserves the full spec for future build.

## 2. Target architecture (Phase 2)

```
Orchestrator [domain: content]
    └── content-lead
        ├── Ingestion & Safety Supervisor
        │   ├── Transcript Worker (Gemini / Whisper)
        │   ├── Platform Compliance Worker (GPT reasoning)
        │   ├── Analytics Worker (GPT — virality scoring)
        │   └── Audio Bleeper (Python/FFmpeg)
        └── Production & Publishing Supervisor
            ├── Spanish Caption Worker (Claude)
            ├── Dynamic Renderer (Remotion/React)
            ├── HITL Approval Gate (n8n webhook pause)
            └── Multi-Platform Publisher (n8n Graph APIs)
```

## 3. Key requirements (preserved from spec)

### Compliance (early filter)
- Scan transcript against YouTube Shorts, TikTok, IG Reels TOS
- Apply risk score to timestamp candidates
- Prefer safer timestamps when virality vs. risk tradeoff exists
- Bleep minor profanity using word-level Whisper timestamps

### Animated captions
- Use Remotion (React-based video canvas), not plain FFmpeg subtitles
- Support multiple animation styles for A/B testing (bouncy, neon, minimal)
- 9:16 aspect ratio, safe-zone caption placement
- Log chosen style to wiki for performance correlation

### HITL publishing (mandatory)
- System MUST NOT auto-post without approval
- Push clip + metadata to staging (Discord/Slack/Monday/local folder)
- Pause orchestrator at `awaiting_hitl_approval`
- Resume on HTTP POST approval callback
- Then trigger n8n multi-platform distribution

## 4. Model routing (Phase 2)

| Worker | Model | Why |
|--------|-------|-----|
| Transcript | Gemini (large context) or Whisper API | Full livestream ingestion |
| Compliance + Analytics | GPT reasoning | Strict policy adherence + scoring |
| Spanish translation | Claude | Natural localized prose |
| Renderer | Remotion (no LLM) | Programmatic video output |

## 5. Integration points in MAS

When Phase 2 begins:

1. Add workers under `scripts/workers/content/`
2. Wire `content` domain in `orchestrator/domains.yaml` from `stub` to `active`
3. Add Remotion project under `templates/content-pipeline/remotion/`
4. Create n8n webhook stubs for HITL gate

## 6. Related wiki pages

- CRM/scheduling eval: `~/Upwork/llmwiki/CRM/entities/`
- Content strategy: Global KB content marketing pages

## 7. Execution instructions (when activated)

1. Build Python transcription wrapper first (Whisper API)
2. Build compliance scorer with platform rule files
3. Scaffold Remotion templates for 3 caption styles
4. Wire HITL gate before any publisher node
5. Update TASKS.md deferred section to track progress

**For now:** No code changes. Reference this prompt when Phase 2 starts.
