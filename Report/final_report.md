# Agentic AI for Automated Digital Marketing
## Campaign Generation, Scheduling, and Management

**University of Greenwich · MSc Computer Science**

| | |
|---|---|
| **Student** | Aniket |
| **Student ID** | 001504619 |
| **Supervisor** | Ayodeji Ibitoye |
| **Submission** | August 2026 |

**Keywords:** Agentic AI · Multi-Agent Orchestration · Digital Marketing Automation · Human-in-the-Loop AI · LangGraph · Content Generation · Social Media Scheduling

---

## Contents

1. [Abstract](#abstract)
2. [Introduction](#1-introduction)
3. [Literature Review](#2-literature-review)
4. [System Design and Methodology](#3-system-design-and-methodology)
5. [Implementation](#4-implementation)
6. [Results and Evaluation](#5-results-and-evaluation)
7. [Discussion](#6-discussion)
8. [Conclusion and Future Work](#7-conclusion-and-future-work)
9. [References](#references)

---

## Abstract

For small and medium-sized businesses, one of the most persistent friction points in digital marketing is the gap between knowing what needs to be posted and actually getting it done. Producing brand-consistent social content at scale calls for four distinct skills working in concert — strategic planning, copywriting, visual asset production, and timely scheduling — that most SMBs can only access piecemeal. Distribution platforms such as Hootsuite and Buffer assume polished content already exists; AI writing tools such as Jasper and Copy.ai can draft individual posts but have no awareness of scheduling infrastructure or the need for campaign-level coherence across multiple days. No commercial product currently stitches all four capabilities into a single, agent-driven workflow.

This project examines whether a multi-agent LLM system can take a brand brief all the way through to a set of scheduled social media posts, with structured human sign-off retained at every content decision. Built on LangGraph, the system offers two orchestration modes: a sequential pipeline (Config A), in which a Strategy Agent hands a complete campaign plan to a Content Agent; and a hierarchical pattern (Config B), in which an Orchestrator Agent dispatches parallel platform-specialist sub-agents. Two research questions guide the study: RQ1 asks how the choice of orchestration architecture shapes the quality of AI-generated content, as judged by independent blind evaluators; RQ2 asks whether the architecture also changes the rate and character of editorial intervention required during human review.

Given a brand description, the system generates a seven-day content calendar — captions and images for Instagram and LinkedIn — in roughly 90 seconds. A browser-based review panel lets users approve, reject, edit, or regenerate any post; every action is recorded in an interaction log for later analysis. Three blind evaluators, each rating a different campaign pair independently, gave Config A a mean Overall Quality score of 3.58/5.00 against 3.40/5.00 for Config B — a direction that held across all three raters without exception. The interaction logs told a complementary story: Config B posts required caption edits on 57% of Instagram posts, against 43% for Config A, and the nature of those edits pointed to a structural rather than stochastic cause — the same phrasing appearing independently across non-adjacent posts, a signature of parallel agents converging without any inter-agent awareness.

The work adds empirical evidence on orchestration architecture choices to a literature that has, until now, drawn almost exclusively on coding and reasoning benchmarks. The central finding — that a more complex, hierarchical architecture underperformed a simpler sequential pipeline precisely because its parallel agents lacked any mechanism for sharing in-progress outputs — has direct implications for anyone designing multi-agent content systems.

**Keywords:** Agentic AI, Large Language Models, Multi-Agent Orchestration, Digital Marketing Automation, Human-in-the-Loop AI, LangGraph, Content Generation, Social Media Scheduling.

---

## 1. Introduction

### 1.1 Background and Motivation

Running a social media presence that builds genuine brand recognition is, for most small and medium-sized businesses (SMBs) and direct-to-consumer brands, a harder operational problem than it first appears. It demands four distinct competencies working in concert: strategic planning (settling on what to post and when), copywriting (writing captions that hook an audience), visual production (generating imagery that reinforces the message), and scheduling (timing publication for maximum reach). In practice, SMBs that cannot sustain all four either outsource to an agency at significant cost or end up posting sporadically — neither approach reliably builds a recognisable brand presence.

The tools available in this space address pieces of the puzzle without connecting them. Scheduling platforms — Hootsuite, Buffer, and Later are the market leaders — handle publication reliably but assume polished content is already queued; they offer no content-generation capability. AI copywriting assistants, chiefly Jasper and Copy.ai, can turn a brief into a usable post in seconds, but they have no ties to a publishing backend, no sense of multi-day campaign arc, and no mechanism for producing visual assets alongside copy. Predis.ai is the one commercial product that attempts to combine generation and scheduling, but it does so as a monolithic system: a single-agent architecture with no configurable orchestration and no structured human review step.

What is absent is not just a feature addition to an existing tool — it is a different architectural paradigm. An integrated, brand-coherent campaign planner that works across multiple platforms and multiple days must be able to break a creative brief into constituent sub-tasks, coordinate those sub-tasks across specialist components, and remain open to correction at each stage. Those are exactly the capabilities that multi-agent LLM systems have started to make tractable since 2022.

AutoGen, MetaGPT, LangGraph, and CrewAI have each demonstrated that networks of LLM-powered agents can take on complex multi-step tasks — decomposing work, calling external APIs, and routing outputs between specialist components in structured ways (Wang et al., 2024; Wu et al., 2023; Hong et al., 2024). The limitation of this literature, however, is its near-exclusive focus on coding and logical reasoning. Whether one agent configuration outperforms another at writing passing tests or solving mathematical problems can be measured automatically; the same certainty is not available in digital marketing, where content quality is judged on brand alignment, platform-native tone, and the harder-to-name quality of posts that feel worth sharing. No empirical work had tested multi-agent architectures in this creative domain.

This project fills that gap. A multi-agent LLM system is designed, built, and evaluated for automated digital marketing campaign generation and scheduling across Instagram and LinkedIn. Two orchestration patterns are implemented — a sequential pipeline and a hierarchical delegation model — and compared empirically. A structured HITL review interface is built into the application from the outset, and every editorial action taken during review is logged, yielding a dataset for quantitative analysis of how architecture shapes both content quality and the burden placed on human reviewers.

### 1.2 Research Questions

This project is guided by two primary research questions:

**RQ1:** How does the choice of multi-agent orchestration pattern (sequential pipeline versus hierarchical delegation) affect the quality, coherence, and brand consistency of AI-generated marketing campaigns, as measured by blind expert evaluator assessment?

**RQ2:** To what extent does the choice of orchestration architecture affect the nature and frequency of human-in-the-loop intervention during content review, and what patterns of editorial action emerge across the two configurations?

### 1.3 Objectives

1. Conduct a systematic literature review of multi-agent LLM architectures, AI content generation, human-in-the-loop design, and social media automation tools, establishing the theoretical framework and identifying the research gaps addressed by RQ1 and RQ2.
2. Design a multi-agent system architecture with two configurable orchestration patterns — sequential pipeline and hierarchical delegation — grounded in the agentic AI literature.
3. Implement the content generation pipeline (text captions and AI images) with a human-in-the-loop review interface and comprehensive interaction logging.
4. Implement post scheduling infrastructure with mock interfaces for multiple platforms.
5. Evaluate the system through a structured experimental framework comparing orchestration patterns and measuring the impact of human-in-the-loop feedback using expert evaluators and interaction log analysis.
6. Document findings, discuss limitations, and propose directions for future research and development.

### 1.4 Report Structure

Chapter 2 reviews five relevant bodies of literature and identifies the research gap. Chapter 3 describes the system design and methodology, including architectural decisions, technology selection, and legal-ethical considerations. Chapter 4 documents the implementation in detail. Chapter 5 presents the evaluation framework and results. Chapter 6 discusses findings in the context of the literature. Chapter 7 concludes with a summary of objectives achieved and directions for future work.

---

## 2. Literature Review

### 2.1 Introduction

The emergence of large language model (LLM)-based agentic systems has opened a new frontier in artificial intelligence research, extending beyond passive text generation into active, tool-using, goal-directed behaviour. Since 2022, frameworks such as AutoGen, MetaGPT, CrewAI, and LangGraph have demonstrated that AI systems can decompose complex tasks, coordinate across multiple specialised sub-agents, and interact with external APIs in pursuit of defined objectives (Wang et al., 2024; Xi et al., 2023). The conceptual groundwork was laid by Brown et al. (2020), who demonstrated that large-scale language models could generalise to unseen tasks without fine-tuning — a prerequisite for the flexible, goal-directed behaviour that modern agent frameworks exploit. This body of work has been primarily focused on coding, reasoning, and knowledge-retrieval tasks; creative domains, particularly digital marketing, remain comparatively underexplored (Davenport et al., 2020).

This review examines five relevant streams of research: (1) LLM-based agent frameworks; (2) multi-agent orchestration patterns; (3) AI content generation; (4) social media automation tools; and (5) human-in-the-loop design principles.

### 2.2 LLM-Based Agent Frameworks

#### 2.2.1 Foundational Paradigms

Chain-of-thought prompting, formalised by Wei et al. (2022), demonstrated that eliciting models to articulate intermediate reasoning steps substantially improved performance on complex tasks. Building on this, Yao et al. (2023) introduced the ReAct framework, which interleaves natural language reasoning with action execution in an iterative loop, establishing the architectural pattern that most modern frameworks have since adapted.

#### 2.2.2 Multi-Agent Frameworks

Wu et al. (2023) introduced AutoGen, a framework enabling multiple LLM-powered agents to communicate in structured conversation threads, with each agent capable of invoking tools, writing and executing code, or deferring to human input. Hong et al. (2024) extended this direction with MetaGPT, which introduced a role-based multi-agent architecture modelled on software engineering team structures, assigning distinct professional roles to individual agents and enforcing structured outputs at each stage. LangGraph models workflows as directed graphs with explicit state management at each node (Wang et al., 2024), while CrewAI allows developers to define agent roles and goals in natural language (Chase, 2023). Dwivedi et al. (2023) surveyed growing practitioner interest in these systems, documenting both productivity potential and persistent concerns around output consistency and factual reliability.

#### 2.2.3 Framework Comparison

Considered comparatively, the frameworks differ substantially in their suitability for a creative marketing application. AutoGen's conversation-based architecture offers flexibility but lacks enforced output structure. MetaGPT's role-based architecture improves reliability but constrains creative flexibility. LangGraph's explicit state management suits iterative campaign workflows. None of these frameworks has been benchmarked on creative or marketing tasks: all performance claims derive from coding or reasoning evaluations where correctness is binary — a fundamentally different quality standard from brand-aligned creative content.

### 2.3 Multi-Agent Orchestration Patterns

#### 2.3.1 Sequential Pipeline Architecture

The sequential pipeline pattern routes task execution through a linear series of specialised agents, where the output of each agent constitutes the input of the next. This pattern is predictable, auditable, and relatively straightforward to debug. Its central limitation is the propagation of upstream errors with no internal mechanism for correction — what this review terms *semantic drift*: small misinterpretations of a brand brief by an upstream agent compound across the pipeline, producing content that is technically coherent but strategically misaligned.

#### 2.3.2 Hierarchical Delegation Architecture

Hierarchical delegation introduces an orchestrating agent that distributes sub-tasks to specialist agents and synthesises their outputs. While this architecture offers significant flexibility, it introduces *orchestrator overhead*: the coordinator agent acts as both a single point of failure and a computational bottleneck. Frameworks like LangGraph attempt to mitigate this through a shared global state object accessible to all agents, reducing redundant data passing (Wang et al., 2024).

#### 2.3.3 Empirical Evidence and Gaps

Empirical evidence on the relative performance of these patterns is limited and domain-specific. Existing benchmarks assess performance on objectively verifiable tasks. Zheng et al. (2023) proposed the LLM-as-a-judge paradigm as a step towards open-ended quality assessment, demonstrating that model-based evaluation can achieve high agreement with human preferences on conversational tasks. Traditional metrics such as BLEU or ROUGE are insufficient for evaluating creative marketing content where brand alignment matters more than lexical similarity. This study therefore prioritises expert human evaluation, utilising Cohen's kappa (Cohen, 1960) to ensure inter-rater reliability.

### 2.4 AI Content Generation: Text and Images

#### 2.4.1 Text Generation

Current large language models are capable marketing writers in a narrow sense: they can produce captions, product descriptions, and campaign copy at speed. Ouyang et al. (2022) demonstrated that fine-tuning on human preference data through reinforcement learning from human feedback substantially improved instruction-following and alignment with user intent. The persistent challenge is prompt sensitivity: small changes to a prompt can shift outputs substantially, creating problems when brand consistency is the objective (Wang et al., 2024).

#### 2.4.2 Image Generation

Rombach et al. (2022) introduced the latent diffusion model architecture underlying Stable Diffusion, achieving high-resolution image synthesis at substantially reduced computational cost. Subsequent developments, including DALL-E 3 (OpenAI, 2023), have further improved prompt adherence and compositional coherence. Despite these advances, brand consistency across generated assets remains a largely unsolved problem: text prompts alone cannot guarantee adherence to a specific colour palette or product geometry.

### 2.5 Social Media Automation Tools

The social media management market is commercially mature but functionally incomplete (Davenport et al., 2020). Scheduling platforms — Hootsuite, Buffer, and Later — handle distribution efficiently but assume content already exists. AI copywriting tools, including Jasper and Copy.ai, address creation but not distribution. Predis.ai combines basic AI generation with scheduling but operates as a monolithic system with no orchestration layer and no structured human review workflow. No current commercial tool combines autonomous content generation, scheduling, and structured human review within a single agentic workflow.

### 2.6 Human-in-the-Loop AI Systems

Amershi et al. (2019) identified eighteen design principles for effective human-AI collaboration, central to which is the idea that AI systems should make uncertainty visible and support correction efficiently. The design of the review interface in this project — with explicit approve, edit, and regenerate options per post — directly reflects these principles. Ouyang et al. (2022) demonstrated that human preferences captured through reinforcement learning from human feedback can be used to fine-tune model behaviour. Shinn et al. (2023) showed that agents equipped with structured self-reflection mechanisms consistently outperform those without them, reinforcing the rationale for integrating human review as a first-class system component.

### 2.7 Research Gap and Conclusion

Research on multi-agent LLM systems has progressed rapidly, with multiple frameworks proposing and validating different orchestration architectures. However, this work has been almost exclusively concentrated on coding, reasoning, and knowledge tasks. The creative domain of digital marketing, where quality is inherently subjective, has received no comparable empirical attention (Davenport et al., 2020; Xi et al., 2023). The phenomena termed *semantic drift* and *orchestrator overhead* represent theoretically distinct risks that have not been empirically measured within any creative application domain. By empirically comparing orchestration patterns and evaluating structured human-in-the-loop mechanisms in a real marketing context, this project addresses a clear and timely gap in both AI systems research and marketing automation practice.

---

## 3. System Design and Methodology

### 3.1 Overall Architecture

The system is designed as a full-stack web application with a clear separation of concerns: an agentic backend responsible for campaign generation, a relational database for persistence, and a React-based frontend for human review and management. The user submits a brand brief through the frontend. The FastAPI backend creates a calendar record and immediately returns a 201 response. Content generation proceeds asynchronously in a background task: the LangGraph pipeline runs the appropriate orchestration configuration, populating the database with structured post data. In parallel, image generation requests are dispatched with a concurrency limit. The frontend polls the backend every three seconds until the calendar status transitions from "generating" to "ready".

### 3.2 Agent Pipeline Design

#### 3.2.1 Sequential Pipeline — Configuration A

In the sequential configuration, a shared `CampaignState` object flows through two nodes in a fixed order. The Strategy Node receives the brand input and first constructs a brand visual style guide — a concise photography and design brief anchored to the specific brand — before generating a full content calendar: for each day and platform, a content theme, platform-optimised caption (including hashtags), and a detailed image prompt grounded in the visual style guide. The Content Node receives the complete plan and generates images for each post. This matches the ReAct-inspired sequential pipeline documented by Yao et al. (2023).

#### 3.2.2 Hierarchical Delegation — Configuration B

In the hierarchical configuration, an Orchestrator Node receives the brand brief and performs two preparatory steps: first constructing the same visual style guide as Config A (ensuring a controlled comparison), then generating a structured strategic brief for each platform — a 2–3 sentence instruction specifying the day-by-day theme progression, platform-specific tone, and one content tactic. These platform briefs are generated simultaneously in a single LLM call.

The orchestrator then launches parallel platform sub-agents — one per platform — via `asyncio.gather`. Each sub-agent is a specialist: it receives only its own platform brief, the shared visual style guide, and the brand description, and generates all *n* posts for its platform independently, without knowledge of any other sub-agent's output. A synthesiser step merges all platform outputs and sorts by day. The Content Node then generates images for each post, identical to Config A.

The key experimental difference is that Config A's strategy pass plans all platforms simultaneously within a single context window, while Config B's sub-agents generate in isolation. Config B introduces an orchestration overhead of two additional LLM calls (style guide + platform briefs) versus Config A's single strategy call, but its design intent is that specialist sub-agents, focused exclusively on one platform, produce more platform-native content.

### 3.3 Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Orchestration framework | LangGraph 0.1 | Explicit state management; supports both sequential and hierarchical topologies within the same codebase |
| LLM — text | OpenAI GPT-4o | Strong instruction-following; consistent JSON output; best-in-class marketing copy quality |
| Image generation | OpenAI gpt-image-1 / Pollinations.ai (fallback) | High prompt adherence; no additional API key required for fallback |
| Backend | FastAPI + Python 3.11 | Async-native; automatic OpenAPI docs; Pydantic v2 validation |
| Database | SQLite (dev) / PostgreSQL (prod) | SQLAlchemy ORM abstracts provider; single connection-string change to migrate |
| Frontend | React 18 + TypeScript + Vite | Component model suits card-per-post review layout; fast HMR during development |
| Styling | TailwindCSS | Rapid prototyping; consistent design system |

### 3.4 Human Review Interface Design

The human review interface is designed in alignment with Amershi et al.'s (2019) eighteen design principles for human-AI interaction. Three principles shaped the interface most directly. *Make clear what the system can and cannot do:* each post card clearly labels content as AI-generated. *Support efficient correction:* approve, reject, edit caption, and regenerate actions are all accessible directly from the post card without navigation. *Scope services when in doubt:* the interface defaults to a "pending" status for all posts, ensuring no content is published without explicit approval. The interface presents posts in a day-tabbed layout, allowing users to assess strategic coherence across days.

### 3.5 Data Model and API Design

Three primary data models support the system. The **Calendar** model stores the brand brief, orchestration configuration, generation timestamps, and status (generating / ready / error). The **Post** model stores one record per day per platform, comprising caption, image URL, image prompt, day, platform, and status (pending / approved / rejected / scheduled). A third model, **InteractionLog**, captures every human action in the review interface: campaign ID, post day, platform, action type (approve / reject / edit_caption / regenerate / schedule), orchestration mode, caption before, caption after, and timestamp. This model is the primary data source for RQ2 analysis.

### 3.6 Legal, Social, Ethical, and Professional Considerations

All data handling complies with the UK GDPR and the UK Data Protection Act 2018. No personal consumer data is collected. Evaluation participant data is anonymised. All participants provided informed consent. API integrations operate in compliance with each provider's terms of service. API keys are stored in environment variables and never committed to version control. The legal status of AI-generated content is currently unsettled in UK law; the system documentation acknowledges this uncertainty and advises users to seek legal guidance before commercial use. Guardrails are implemented in agent prompts to prevent the generation of false claims, manipulative techniques, or content targeting vulnerable groups.

---

## 4. Implementation

### 4.1 LangGraph Sequential Pipeline

The sequential pipeline is implemented in `backend/src/agents/strategy.py` and `backend/src/agents/content.py`, wired together via a LangGraph `StateGraph`. A `CampaignState TypedDict` defines the shared state object carrying brand input fields, generated posts, and errors. The graph defines two nodes — `strategy_node` and `content_node` — connected by a directed edge. The compiled graph object is instantiated once at module load time and reused across all requests.

The `strategy_node` performs two LLM calls: first a `_build_visual_style_guide` call that analyses the brand and returns a concise photography guide (lighting, colour palette, lens feel, mood, six keyword modifiers, and one example hero shot prompt); then a full content calendar call that receives the style guide and produces a JSON array of posts with caption, hashtags, content type, and image prompt per entry. JSON parsing is retried up to three times before writing an error to state. All captions are post-processed through `strip_day_artifacts()` — a regex function that removes day-numbering artefacts (e.g., "Day 2 at…") that LLMs inject into multi-day calendar prompts.

The `content_node` iterates over all posts and dispatches image generation requests concurrently using `asyncio.gather` with a semaphore limiting concurrency to three simultaneous requests, preventing API rate-limit errors.

### 4.2 Hierarchical Orchestration Pipeline

The hierarchical pipeline is implemented in `backend/src/agents/orchestrator.py`. The `orchestrator_node` performs three sequential steps before handing off to the same `content_node` used by Config A.

**Step 1 — Shared visual style guide.** Identical to Config A: `_build_visual_style_guide` is called with the brand prompt, producing the same structured photography brief. This ensures that any visual quality differences between configurations are attributable to caption content rather than image prompt quality.

**Step 2 — Per-platform strategic briefs.** A single orchestrator LLM call receives the brand brief and platform list, and returns a JSON object mapping each platform name to a 2–3 sentence brief covering: (a) the day-by-day theme progression, (b) the unique tone or angle for that platform, and (c) one platform-specific content tactic. This brief is the only context the sub-agent receives beyond the shared style guide and brand description.

**Step 3 — Parallel sub-agents.** One `_platform_sub_agent` coroutine is launched per platform, all executed concurrently via `asyncio.gather`. Each sub-agent receives its platform brief, the shared style guide, the brand description, and the number of days, and returns a list of Post objects for its platform. Sub-agents have no visibility into each other's output during generation. Each sub-agent invocation is retried up to three times on parsing failure before the platform is skipped with an error written to state. All captions returned by sub-agents are post-processed through the same `strip_day_artifacts()` function as Config A.

**Synthesiser.** All platform post lists are merged and sorted by (day, platform) for deterministic ordering before being written to `state["posts"]` and passed to the content node.

### 4.3 Content Generation Agents

Caption prompts include several design choices grounded in the literature: the brand tone is repeated in both system and user messages to reinforce adherence (Wang et al., 2024); platform-specific character limits and hashtag conventions are enforced in the prompt; and explicit rules prohibit day-numbering in captions and require hook variation across posts. Image generation prompts are engineered to encode visual consistency constraints drawn from the brand style guide, with negative prompt instructions excluding watermarks, text overlays, and illustrations. All image generation uses the `gpt-image-1` model in standard quality mode; base64-encoded responses are decoded and stored as data URIs in the database.

### 4.4 Human-in-the-Loop Interface and Interaction Logging

The review interface is implemented as a React 18 TypeScript single-page application. Each campaign is accessible at `/campaigns/:id`, presenting a tab-per-day layout. Each tab displays all posts for that day as cards with the generated image and caption, hashtags, and action buttons. Five actions are available per post: approve, reject, edit caption (inline text edit), regenerate, and schedule. All five actions trigger an `InteractionLog` record on the backend via the appropriate API endpoint, capturing the campaign ID, post day, platform, action, orchestration mode, and caption state before and after the action.

### 4.5 Backend API

The FastAPI backend exposes endpoints for campaign creation (`POST /campaigns`), campaign status polling (`GET /campaigns/{id}`), post status update (`PATCH /campaigns/{id}/posts/{day}`), regeneration (`POST /campaigns/{id}/posts/{day}/regenerate`), campaign scheduling (`POST /campaigns/{id}/schedule`), and interaction log retrieval (`GET /campaigns/{id}/interactions`). The orchestration mode is specified as a field on the campaign creation request and stored in the Campaign model, allowing the API to route generation to the appropriate LangGraph graph. All endpoints include Pydantic v2 schema validation.

### 4.6 Frontend

The frontend is a single-page application built with React 18, TypeScript, and Vite. React Router v6 provides client-side routing. TailwindCSS provides the visual design system, including responsive grid layouts for post cards, colour-coded status badges (pending / approved / rejected / scheduled), and polling state management. The `api.ts` module centralises all backend communication using the native Fetch API, with error handling and user-facing toast notifications for failures. The polling mechanism uses a `useEffect` hook with a three-second interval cleared when the campaign status transitions from "generating" to "ready".

---

## 5. Results and Evaluation

### 5.1 Evaluation Framework

The evaluation is structured to address both research questions through expert human assessment and user interaction log analysis.

**RQ1 — Orchestration Pattern Comparison.** Three independent evaluators each received a unique campaign run pair (A*n* vs B*n*), comprising 14 posts — 7 Instagram and 7 LinkedIn — generated from the same brand brief for The Morning Press, a fictional specialty coffee shop in Manchester. All evaluators rated posts without knowledge of which configuration produced them. Each post was rated on four criteria using a 1–5 Likert scale: Platform Fit, Brand Voice, Engagement Potential, and Overall Quality.

**RQ2 — Human-in-the-Loop Interaction Analysis.** A single HITL review session was conducted using the live application. The researcher reviewed all 7 Instagram posts from one Config A campaign and one Config B campaign generated from the same brand brief. All approve, edit_caption, regenerate, and schedule actions were recorded automatically by the `InteractionLog` table. LinkedIn posts were reviewed qualitatively but excluded from logged data due to a structural API limitation (the post update endpoint identifies posts by day number only, so LinkedIn actions were indistinguishable from Instagram actions without a platform parameter).

### 5.2 RQ1 — Content Quality Evaluation

#### 5.2.1 Per-Evaluator Results

**Table 5.1 — Per-Evaluator Mean Scores (1–5 scale, 14 posts per set)**

| Evaluator | Run Pair | Plat. Fit A | Plat. Fit B | Voice A | Voice B | Engage A | Engage B | Overall A | Overall B |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Evaluator 1 | A1 / B1 | — | — | — | — | — | — | 3.21 | 3.00 |
| Evaluator 2 | A2 / B2 | 3.43 | 3.21 | 4.00 | 4.00 | 3.00 | 3.07 | 3.43 | 3.21 |
| Evaluator 3 | A3 / B3 | 4.20 | 4.00 | 4.00 | 4.00 | 4.10 | 4.00 | 4.10 | 4.00 |
| **Cross-evaluator mean** | **(Overall Quality, n=3)** | | | | | | | **3.58** | **3.40** |

> **Key finding (RQ1):** All three evaluators independently rated Config A higher than Config B on Overall Quality. The mean difference (Δ = 0.18) favours the sequential pipeline across independent evaluators rating different campaign runs.

#### 5.2.2 Criterion-Level Analysis

**Table 5.2 — Mean Scores by Criterion (Evaluators 2 & 3, n=28 posts per config)**

| Criterion | Config A | Config B | Δ (A − B) |
|---|:---:|:---:|:---:|
| Platform Fit | 3.82 | 3.61 | +0.21 |
| Brand Voice | 4.00 | 4.00 | 0.00 |
| Engagement Potential | 3.55 | 3.54 | +0.01 |
| Overall Quality | 3.77 | 3.61 | +0.16 |

Platform Fit produced the widest spread (Δ = 0.21) — and in the direction that contradicts Config B's design rationale, since its platform-dedicated agents scored below the generalist planner. Brand Voice came out identical on both sides, suggesting brand tone is fixed at brief level and is not moved by architectural choice. Engagement Potential sat at the bottom of the scale for both configurations, marking a shared limitation that orchestration architecture alone cannot address.

#### 5.2.3 Inter-Rater Variation

Evaluator 3 tended to score in the 4–5 range; Evaluators 1 and 2 concentrated around 3–4. This scale-usage divergence is a familiar artefact of subjective text assessment, where individual anchoring habits vary in the absence of a shared calibration exercise. It does not compromise the primary result: within each rater, the ordering was A > B in every case, with margins running from Δ = 0.10 to Δ = 0.22 — consistent enough to support the directional conclusion even against the backdrop of absolute-score differences across raters.

#### 5.2.4 Qualitative Evaluator Observations

Both evaluators who left written comments flagged the same two problems. First, both configurations over-leaned on a narrow vocabulary — words like "sanctuary," "hustle and bustle," and "third space" recurred enough to be noticeable. Second, Config B's captions carried day-numbering phrases, such as "Day 2 of finding your perfect pour-over," that read as calendar artefacts rather than standalone social posts. It was this second issue — a structural output from how sub-agents frame multi-day sequences — that both evaluators specifically named as the reason for Config B's lower Platform Fit ratings.

> *"Set A was slightly higher quality overall because it adapted more naturally between Instagram and LinkedIn posts with fewer intrusive calendar artefacts."*
> — Evaluator 2

> *"Set B was excellent but more uniform in its quality, lacking the same level of 'wow factor' and platform-specific nuance that the best posts in Set A achieved."*
> — Evaluator 3

### 5.3 RQ2 — Human-in-the-Loop Interaction Analysis

| Metric | Config A | Config B |
|---|:---:|:---:|
| Edit rate | **43%** (3 of 7) | **57%** (4 of 7) |
| Regeneration rate | **14%** (1 of 7) | **0%** |

**Table 5.3 — HITL Action Summary (Instagram posts, n=7 per config)**

| Action | Config A | Config B |
|---|:---:|:---:|
| Clean approvals (no edit) | 4 (57%) | 3 (43%) |
| Caption edits | 3 (43%) | 4 (57%) |
| Regenerations | 1 (14%) | 0 (0%) |
| Rejections | 0 (0%) | 0 (0%) |
| Posts scheduled (total) | 7 (100%) | 7 (100%) |

> **Key finding (RQ2):** Config B required a higher rate of editorial intervention (57% edited) compared to Config A (43%). Both configurations achieved a 100% schedule rate, indicating both pipelines produce content ultimately acceptable for publication. The difference lies in human effort required to reach that outcome.

Beyond the headline rate, what the reviewer was correcting differed markedly between configurations. Config A's edits were reactive to individual post problems — a metaphor that appeared once too often, a hashtag block that felt heavy. For Config B, three of the four edits addressed the same underlying issue: the construction "diving into X or diving into Y" appearing in posts on non-adjacent days, each generated by a different sub-agent invocation with no knowledge of the others. The repetition was not a stylistic accident; it was a coordination failure written into the outputs by the architecture itself.

The qualitative read of LinkedIn posts — not included in the logged dataset but reviewed alongside the Instagram posts — reinforced the same picture. Three of Config B's LinkedIn posts, written on non-adjacent days, had independently landed on a "redefine productivity" framing that sat at odds with the brand brief's explicit instruction to avoid corporate language. Config A's LinkedIn posts moved across different themes across the seven days, suggesting that planning all platforms within a single context window naturally produced more varied outputs.

> **Methodological note:** The post update and regeneration endpoints identify posts by day number only, without a platform parameter. To preserve data integrity, LinkedIn post actions were excluded from the logged dataset. Additionally, the HITL session was conducted by the researcher with knowledge of configuration labels, introducing potential reviewer bias.

---

## 6. Discussion

### 6.1 The Counterintuitive Cost of Specialisation (RQ1)

#### 6.1.1 Platform fit: why the specialist sub-agents underperformed

RQ1's most striking result — and its most theoretically significant — is that Config B's platform-specialist sub-agents scored *below* Config A's generalist planner on Platform Fit (Δ = 0.21). The premise of Config B is that dedicating one agent exclusively to Instagram should produce more platform-appropriate content than a single agent splitting its attention across both platforms. The data says otherwise.

Task decomposition theory offers an explanation. Brooks (1995) observed, writing about software engineering teams, that splitting work across independent specialists inevitably introduces coordination and integration costs that can cancel out — or even reverse — the specialisation dividend. In Config B, each sub-agent received only its own platform brief and had no visibility into what its counterparts were producing. When a single agent plans both Instagram and LinkedIn, it implicitly contrasts them; when two separate agents plan from the same thematic inputs in isolation, they tend toward similar framings, with nobody in the system positioned to notice the redundancy. Hong et al. (2024) documented precisely this dynamic at the framework level: multi-agent systems outperform single-agent equivalents only when inter-agent communication is substantive. Config B's sub-agents communicated with each other not at all.

#### 6.1.2 Brand voice invariance

Both configurations earned identical Brand Voice ratings of 4.00 — a notable null result that points toward a prompt-level rather than architecture-level explanation. Brand tone appears to be captured or lost at the brief-writing stage: a well-specified persona instruction is absorbed by an instruction-tuned model regardless of whether that model sits in a sequential or hierarchical graph (Ouyang et al., 2022). For practitioners, this carries a practical implication: if the goal is brand-consistent AI output, the effort is better directed at improving brief specificity than at adding orchestration layers.

#### 6.1.3 The engagement ceiling

Engagement Potential was the weakest-scoring dimension for both configurations — 3.55 for Config A and 3.54 for Config B — with a gap of essentially zero. The consistency of this low score across two architecturally distinct systems points to a model-level ceiling rather than an orchestration problem. Instruction-tuned LLMs produce grammatically clean, tonally appropriate text; they tend to avoid the rhetorical risks — the unexpected hook, the slightly subversive angle — that make social content genuinely shareable. Pavlik (2023) describes this pull toward 'safe, generic expression' as a structural feature of current generative AI. Changing the topology of the agent graph does not change the generative model underneath it, and neither architecture was able to overcome this floor.

#### 6.1.4 Inter-rater variation

Across the three evaluators, a leniency effect was visible: Evaluator 3 clustered responses in the 4–5 range, while Evaluators 1 and 2 occupied the 3–4 range. Krippendorff (2004) identifies individual scale-usage tendencies as one of the most reliable sources of variance in subjective text quality assessments, and the absence of a shared calibration exercise before rating almost certainly amplified this. What matters for the primary conclusion is the within-rater ordering, not the absolute values: all three raters independently placed Config A above Config B, with margins ranging from Δ = 0.10 to Δ = 0.22. The relative result holds; the absolute numbers should be read as directional indicators from a small, heterogeneous sample rather than as stable population estimates.

### 6.2 The Human Cost of Coordination Failure (RQ2)

#### 6.2.1 Edit rate as a proxy for content coherence

Config B's 57% edit rate against Config A's 43% can be read as the human labour cost of the coordination failure described in Section 6.1.1. A reviewer reading posts one at a time might not notice that three non-adjacent days share the same sentence construction; reading a week of content end-to-end, the pattern becomes obvious and triggers a correction. That correction burden — avoidable in principle had the architecture included cross-post awareness — was systematically higher for Config B. Amershi et al. (2019) argue that well-designed AI systems should proactively avoid generating outputs that predictably require human correction; Config B's architecture, by construction, generated exactly such outputs.

#### 6.2.2 Local versus systemic failure

The type of edit, not just its rate, distinguishes the two configurations. Config A's edits were one-off: a metaphor overused in a single post, an emoji count that felt excessive — the sort of mistakes that will differ across campaign runs, random variation in stochastic text generation. Config B's edits addressed a repeating pattern: the same verb construction appearing in posts generated by three separate sub-agents on non-adjacent days, each arriving at it independently. Liang et al. (2023) call this independent agent mode collapse — parallel agents, drawing on the same underlying model, converge on a locally favoured expression even without coordinating, producing what looks like deliberate repetition but is a shared blind spot. Prompt-level changes can address isolated post failures; failures of this structural kind require changing the architecture.

#### 6.2.3 The human as safety net

Every post from both configurations was ultimately scheduled — a 100% publishability rate. Shneiderman (2022) describes the human reviewer in HITL systems as providing a quality floor: whatever the AI produces, the human's corrections ensure the final output meets a minimum standard before publication. What the raw RQ1 scores measure, then, is not the quality of the content users actually post — it is the quality of the first draft they receive. After editing, the gap between Config A and Config B likely narrows. The architectures differ not in eventual published quality, but in how much editorial work is required to get there.

### 6.3 Integrating RQ1 and RQ2

Read together, the RQ1 and RQ2 data converge on a single story about coordination cost. Config B's hierarchical structure rests on an intuition borrowed from organisational theory: that specialists directed by a coordinator should outperform generalists working across the full scope of a task. This intuition — sound for human teams — does not translate cleanly to parallel LLM sub-agents with no communication channel between them during generation. They are handed their briefs in one pass, produce their outputs in isolation, and deliver everything to a synthesiser that re-orders by day but exercises no editorial judgement over cross-platform coherence.

> **Central finding:** The sequential pipeline's apparent simplicity is, in this domain, a functional advantage. Config B's problems arise not from specialist incompetence but from insufficient inter-agent communication — a coordination failure that a sequential, globally-aware agent naturally avoids by planning all platforms within a single context window. This is consistent with Wu et al.'s (2023) finding that multi-agent architectures excel at tasks where subtask outputs are *independently verifiable and composable*; social media campaigns, where cross-post coherence is an explicit quality requirement, may be precisely the task type where composability breaks down.

### 6.4 Limitations

> **Sample size:** The evaluation involved three evaluators rating 42 posts per configuration. The observed Δ = 0.18 on a 5-point scale is small in absolute terms; without a power analysis, it is not possible to determine whether this difference would replicate at scale. All RQ1 findings should be treated as hypothesis-generating rather than confirmatory.

> **Single domain:** All campaign runs used the same brand brief. It is not known whether the relative performance of Config A and Config B would hold for brands with different brief characteristics or a wider platform mix.

> **Researcher bias in HITL:** The RQ2 data was collected by the researcher with knowledge of configuration labels. A fully blinded HITL study would provide stronger evidence for the interaction rate difference.

> **API structural limitation:** The absence of a platform parameter in post update endpoints meant that LinkedIn interactions could not be reliably logged, likely understating the true edit rate difference between configurations.

### 6.5 Implications

**Cross-agent context sharing**
- Parallel sub-agents should share in-progress outputs before finalising, enabling active differentiation rather than independent convergence.
- A shared "coverage log" tracking phrases and constructions already used could be passed to each sub-agent to actively avoid repetition.

**Synthesiser as editor**
- Extending the Config B synthesiser from merge-and-sort to active cross-post consistency checking would address the systemic failure identified in RQ2.

**Brief quality over architecture**
- Brand Voice invariance across both configurations suggests that structured brand brief templates yield higher quality returns than architectural complexity.

**API completeness**
- All post-level API endpoints should include a platform parameter to support reliable HITL logging in multi-platform campaigns.

---

## 7. Conclusion and Future Work

### 7.1 Summary of Objectives Achieved

- **Objective 1 — Literature review** ✅ Completed. Five streams of relevant research examined; dual research gap identified and theoretical framework established.
- **Objective 2 — System architecture** ✅ Completed. Both the sequential pipeline (Config A) and hierarchical delegation (Config B) are fully designed and implemented in a single codebase, enabling controlled comparison.
- **Objective 3 — Content pipeline and HITL logging** ✅ Completed. The end-to-end pipeline (brand brief → 7-day calendar → AI captions + images → human review) is fully functional. The InteractionLog system captures all HITL action types with timestamps and before/after content.
- **Objective 4 — Scheduling infrastructure** ✅ Partially completed. Campaign scheduling is implemented and functional for the evaluated platforms (Instagram and LinkedIn mock scheduling). Direct Meta Graph API publishing was deferred as out of scope for the evaluation.
- **Objective 5 — Evaluation** ✅ Completed. Three blind evaluators rated 42 posts per configuration across RQ1; a HITL interaction session was logged and analysed for RQ2.
- **Objective 6 — Final report** ✅ Completed by this document.

### 7.2 Broader Contribution

Three contributions follow from this work. The first is empirical: to the best of the author's knowledge, this is the first published comparison of sequential and hierarchical multi-agent orchestration patterns evaluated in a creative content domain. The gap was noted by Wang et al. (2024) and Wu et al. (2023), who each called for evaluation beyond code and reasoning tasks. The finding — that hierarchical parallel dispatch underperforms sequential global planning when sub-agents operate in isolation — is a precise and actionable result for system designers.

The second contribution is methodological. A four-dimension evaluator rubric (Platform Fit, Brand Voice, Engagement Potential, Overall Quality) combined with structured interaction log analysis constitutes a reusable evaluation framework for creative agentic systems. The apparatus developed here could be applied, without fundamental change, to future work on AI-assisted content workflows in journalism, advertising, or product design.

Third, the system itself is a working prototype. It shows that a full digital marketing pipeline — from brand brief to scheduled post — can be automated under multi-agent LLM control while keeping a human meaningfully in the loop at each content decision. The design is not specific to marketing: any domain requiring structured, multi-step creative output with iterative human approval could adopt the same architectural pattern.

### 7.3 Future Work

| Direction | Description |
|---|---|
| **Communicative sub-agents** | Allow Config B's parallel sub-agents to exchange draft outputs before finalising, enabling active differentiation and testing whether this eliminates the convergence failure observed. |
| **RLHF from interaction logs** | The before/after content pairs in the InteractionLog table constitute a preference dataset for fine-tuning the caption generation model, potentially reducing intervention rates over time. |
| **Blinded HITL study** | Replicate the RQ2 study with an operator who does not know configuration labels to eliminate researcher bias from the interaction rate comparison. |
| **Wider platform mix** | Extend to Twitter/X (character limits), TikTok (trend-awareness), and Facebook, testing whether Config B's coordination failure is more or less pronounced at greater platform diversity. |
| **Engagement ground truth** | Publish AI-generated posts to real audiences and correlate blind evaluator Engagement Potential ratings with actual engagement metrics (likes, comments, reach). |
| **WhatsApp review interface** | Deliver campaign drafts as WhatsApp messages, allowing SMB users to approve or request revisions through natural language replies without a dedicated web application. |

What this dissertation adds, above all, is a concrete data point: evidence that the intuitions underpinning multi-agent system design — often borrowed wholesale from human organisational theory — do not always survive contact with the realities of parallel LLM execution. In content creation, as perhaps in other creative domains, the choice of orchestration architecture is not merely a software engineering preference. It shapes what humans have to do to make AI-generated output fit to publish.

---

## References

1. Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P. N., Inkpen, K., Teevan, J., Kikin-Gil, R. and Horvitz, E. (2019) 'Guidelines for human-AI interaction', in *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*. Glasgow, UK, 4–9 May. New York: ACM, pp. 1–13.

2. Brooks, F. P. (1995) *The Mythical Man-Month: Essays on Software Engineering* (Anniversary ed.). Addison-Wesley.

3. Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A. and others (2020) 'Language models are few-shot learners', in *Advances in Neural Information Processing Systems (NeurIPS 2020)*, vol. 33, pp. 1877–1901.

4. Brooke, J. (1996) 'SUS: A "quick and dirty" usability scale', in Jordan, P. W., Thomas, B., Weerdmeester, B. A. and McClelland, A. L. (eds.) *Usability Evaluation in Industry*. London: Taylor & Francis, pp. 189–194.

5. Buffer (2024) *Buffer: Social media management platform* [Online]. Available at: https://buffer.com (Accessed: 1 April 2025).

6. Chase, H. (2023) *CrewAI: Framework for orchestrating role-playing, autonomous AI agents* [Online]. GitHub. Available at: https://github.com/crewAIInc/crewAI (Accessed: 1 April 2025).

7. Cohen, J. (1960) 'A coefficient of agreement for nominal scales', *Educational and Psychological Measurement*, 20(1), pp. 37–46.

8. Copy.ai (2024) *Copy.ai: AI-powered copywriting platform* [Online]. Available at: https://www.copy.ai (Accessed: 1 April 2025).

9. Davenport, T., Guha, A., Grewal, D. and Bressgott, T. (2020) 'How artificial intelligence will change the future of marketing', *Journal of the Academy of Marketing Science*, 48(1), pp. 24–42.

10. Dwivedi, Y. K., Kshetri, N., Hughes, L., Slade, E. L., Jeyaraj, A., Kar, A. K., Baabdullah, A. M., Koohang, A., Raghavan, V., Ahuja, M. and others (2023) '"So what if ChatGPT wrote it?" Multidisciplinary perspectives on opportunities, challenges and implications of generative conversational AI for research, practice and policy', *International Journal of Information Management*, 71, p. 102642.

11. Hong, S., Zhuge, M., Chen, J., Zheng, C., Cheng, Y., Zhang, C., Wang, J., Wang, Z., Yau, S. K. S., Lin, Z., Zhou, L., Ran, C., Xiao, L., Wu, C. and Schmidhuber, J. (2024) 'MetaGPT: Meta programming for a multi-agent collaborative framework', in *Proceedings of the 12th International Conference on Learning Representations (ICLR 2024)*. Vienna, Austria, 7–11 May.

12. Hootsuite (2024) *Hootsuite: Social media management and scheduling platform* [Online]. Available at: https://www.hootsuite.com (Accessed: 1 April 2025).

13. Jasper (2024) *Jasper: AI content platform for marketing teams* [Online]. Available at: https://www.jasper.ai (Accessed: 1 April 2025).

14. Krippendorff, K. (2004) *Content Analysis: An Introduction to Its Methodology* (2nd ed.). Sage.

15. Later (2024) *Later: Social media scheduling and visual planning platform* [Online]. Available at: https://later.com (Accessed: 1 April 2025).

16. Liang, T., He, Z., Jiao, W., Wang, X., Wang, Y., Wang, R., Yang, Y., Tu, Z. and Shi, S. (2023) 'Encouraging divergent thinking in large language models through multi-agent debate', *arXiv preprint arXiv:2305.19118*.

17. OpenAI (2023) 'GPT-4 technical report', *arXiv preprint arXiv:2303.08774*. Available at: https://arxiv.org/abs/2303.08774 (Accessed: 1 April 2025).

18. Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A. and others (2022) 'Training language models to follow instructions with human feedback', in *Advances in Neural Information Processing Systems (NeurIPS 2022)*, vol. 35, pp. 27730–27744.

19. Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P. and Bernstein, M. S. (2023) 'Generative agents: Interactive simulacra of human behaviour', in *Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology (UIST 2023)*. San Francisco, CA, 29 October–1 November. New York: ACM, pp. 1–22.

20. Pavlik, J. V. (2023) 'Collaborating with ChatGPT: Considering the implications of generative artificial intelligence for journalism and media education', *Journalism & Mass Communication Educator*, 78(1), pp. 84–93.

21. Predis.ai (2024) *Predis.ai: AI-powered social media content creation and scheduling* [Online]. Available at: https://predis.ai (Accessed: 1 April 2025).

22. Rombach, R., Blattmann, A., Lorenz, D., Esser, P. and Ommer, B. (2022) 'High-resolution image synthesis with latent diffusion models', in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2022)*. New Orleans, LA, 18–24 June, pp. 10684–10695.

23. Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Zettlemoyer, L., Cancedda, N. and Scialom, T. (2023) 'Toolformer: Language models can teach themselves to use tools', in *Advances in Neural Information Processing Systems (NeurIPS 2023)*, vol. 36, pp. 68539–68551.

24. Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K. and Yao, S. (2023) 'Reflexion: Language agents with verbal reinforcement learning', in *Advances in Neural Information Processing Systems (NeurIPS 2023)*, vol. 36, pp. 8634–8652.

25. Shneiderman, B. (2022) *Human-Centered AI*. Oxford University Press.

26. Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J., Chen, Z., Tang, J., Chen, X., Lin, Y., Zhao, W. X., Wei, Z. and Wen, J. R. (2024) 'A survey on large language model based autonomous agents', *Frontiers of Computer Science*, 18(6), p. 186345.

27. Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q. and Zhou, D. (2022) 'Chain-of-thought prompting elicits reasoning in large language models', in *Advances in Neural Information Processing Systems (NeurIPS 2022)*, vol. 35, pp. 24824–24837.

28. Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., Jiang, L., Zhang, X., Zhang, S., Liu, J., Awadallah, A. H., White, R. W., Burger, D. and Wang, C. (2023) 'AutoGen: Enabling next-generation LLM applications via multi-agent conversation', *arXiv preprint arXiv:2308.08155*.

29. Xi, Z., Chen, W., Guo, X., He, W., Ding, Y., Hong, B., Zhang, M., Wang, J., Jin, S., Zhou, E. and others (2023) 'The rise and potential of large language model based agents: A survey', *arXiv preprint arXiv:2309.07864*.

30. Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. and Cao, Y. (2023) 'ReAct: Synergising reasoning and acting in language models', in *Proceedings of the 11th International Conference on Learning Representations (ICLR 2023)*. Kigali, Rwanda, 1–5 May.

31. Zheng, L., Chiang, W. L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E. and Stoica, I. (2023) 'Judging LLM-as-a-judge with MT-Bench and Chatbot Arena', in *Advances in Neural Information Processing Systems (NeurIPS 2023)*, vol. 36, pp. 46595–46623.
