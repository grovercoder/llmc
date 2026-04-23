# LLMC Documentation

Welcome to the LLMC (LLM Chooser) documentation. This guide explains the data structures, concepts, and usage of LLMC.

## Documentation Overview

- [Provider Data Structure](./provider.md) - Configuration for AI service providers
- [Agents Data Structure](./agents.md) - Configuration for coding agents that LLMC syncs with
- [AI Model Data Structure](./aimodel.md) - Configuration for individual AI models

## Core Concepts

LLMC is designed to decouple AI model preferences from individual tools by providing a centralized configuration system. It consists of three main components:

1. **Providers** - AI service providers like Ollama, OpenAI, Anthropic, etc.
2. **Models** - Specific models from those providers that you've selected to use
3. **Agents** - Coding tools and IDE integrations that LLMC can synchronize with

## Getting Started

See the [README.md](../README.md) for installation and basic usage instructions.

## API Reference

For developers looking to extend LLMC, the data structures documented here represent the core models used throughout the application.