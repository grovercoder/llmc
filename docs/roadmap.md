# LLMC Roadmap

This document outlines the planned future development for LLMC (LLM Chooser). The roadmap is subject to change based on community feedback, contributor availability, and evolving needs in the AI tooling landscape.

## Near-Term Goals (Next 1-3 Months)

### TUI Interface Development
- Begin implementation of a Text User Interface (TUI) using libraries like `textual` or `curses`
- Provide an interactive alternative to the CLI for common operations
- Include visual indicators for provider status, model selection, and sync operations

### Enhanced Provider Support
- Add support for additional open-source model providers (e.g., Hugging Face inference endpoints)
- Improve automatic detection of local providers (Ollama, LMStudio, etc.)
- Add provider health checking capabilities

### Expanded Agent Integrations
- Add support for more coding agents (Continue.dev, Zed AI, GitHub Copilot CLI)
- Improve existing agent adapters based on user feedback
- Add bidirectional sync capabilities where agents support it

## Mid-Term Goals (3-6 Months)

### Plugin Architecture
- Develop a plugin system for extending LLMC functionality
- Allow community-contributed provider and agent adapters
- Create a standardized interface for custom synchronization logic

### Advanced Configuration Features
- Implement model grouping and profiles (e.g., "coding", "research", "creative" configurations)
- Add environment-specific configurations (development, staging, production)
- Support for configuration templating and variable substitution

### Improved User Experience
- Add shell completion for bash, zsh, and fish
- Implement configuration validation and migration tools
- Add detailed logging and debugging modes
- Create setup wizard for first-time users

## Long-Term Goals (6+ Months)

### Ecosystem Integrations
- Develop official LLMC extensions for popular IDEs (VS Code, JetBrains)
- Create integrations with AI orchestration platforms
- Add support for model serving platforms (vLLM, TensorRT-LLM, etc.)

### Collaborative Features
- Enable sharing of model configurations within teams
- Add version control integration for configurations
- Implement configuration approval workflows

### Analytics and Insights
- Add usage statistics for models and providers
- Implement cost tracking and optimization suggestions
- Add performance monitoring for different models/providers

## Community Contributions

We welcome contributions from the community! Areas where help is particularly appreciated include:

- **New Provider Adapters**: Adding support for additional AI service providers
- **Agent Synchronization**: Developing adapters for new coding agents
- **Documentation**: Improving guides, tutorials, and examples
- **Testing**: Writing unit and integration tests
- **Translations**: Making LLMC accessible to non-English speakers
- **Tooling**: Improving development experience with better scripts and CI/CD

## How to Stay Updated

- Watch the GitHub repository for release announcements
- Check the CHANGELOG.md for detailed release notes
- Participate in discussions through GitHub Issues
- Contribute directly by opening Pull Requests

---

*Last updated: April 2026*
*This roadmap represents our current plans and may adjust based on technical feasibility, community input, and evolving technology trends.*