# Architecture Documentation

This directory contains the system design documentation for the Co-Agent-Recruitment platform.

## Files

- [`system_design.md`](system_design.md) - Complete system design documentation including architecture diagrams, agent specifications, tool interfaces, and development guidelines
- [`img/high_level.mmd`](img/high_level.mmd) - High-level architecture diagram (Mermaid format)
- [`img/match_sequence.mmd`](img/match_sequence.mmd) - Sequence diagram for candidate-job matching flow (Mermaid format)

## Viewing Diagrams

The Mermaid diagrams can be viewed:
- On GitHub (native Mermaid support)
- Using the [Mermaid Live Editor](https://mermaid.live/)
- In IDEs with Mermaid preview extensions
- Using the `mume` command-line tool

## Architecture Overview

The system follows a layered architecture:

1. **Frontend/UI Layer** - Next.js application with REST API
2. **Orchestration Layer** - ADK-based agent management with session handling  
3. **Core Agents** - Specialized agents for resume parsing, job posting analysis, and matching
4. **Communication Layer** - Google Cloud Pub/Sub for asynchronous agent communication
5. **External Services** - Google Vertex AI, Firestore, Firebase Auth, Cloud Functions

For detailed information, see the [complete system design documentation](system_design.md).