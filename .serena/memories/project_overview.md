# AIレスバ掲示板 (AI Resuba BBS) - Project Overview

## Purpose
An entertainment-focused web application where multiple AI characters engage in automated debate battles (レスバトル). Users enjoy watching the unique interactions between AI personalities.

## Key Concept
"Pure entertainment with zero productivity" - A 2ch-style bulletin board where AI characters argue automatically.

## Project Origin
Based on the OpenArena codebase located at `/Users/teradakousuke/Developer/OpenArena/`. The strategy is to reuse ~80% of the existing code to reduce development time by 70%.

## Main Features
- Automatic thread generation with AI characters
- 2-5 second interval posting by AI characters  
- Anchor functionality (>>number references)
- Debate escalation mechanics
- 30% chance of topic derailment
- LocalStorage persistence for threads

## AI Characters (5 total)
1. **Grok** - Thread starter, sarcastic and provocative
2. **GPT君** - Polite honor student type
3. **Claude先輩** - Logical and cautious
4. **Gemini** - Creative and naturally airheaded
5. **名無しさん** - Random personality

## Development Status
The project has migrated from OpenArena codebase and is implementing AI debate functionality with cloud APIs instead of local Ollama.