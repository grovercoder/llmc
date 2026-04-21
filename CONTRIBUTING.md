# Contributing to LLMC

Thank you for considering contributing to LLMC! We welcome contributions from the community.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Ensure your code follows the project's coding standards
5. Add tests for new functionality
6. Submit a pull request

## Coding Standards

- Follow PEP 8 for Python code
- Use type hints wherever possible
- Write clear, descriptive commit messages
- Keep lines to a maximum of 88 characters (as enforced by black)
- Use descriptive variable and function names

## Development Setup

```bash
# Clone the repository
git clone <your-fork-url>
cd llmc

# Set up the development environment
uv sync

# Install pre-commit hooks (optional but recommended)
pre-commit install

# Run tests
uv run pytest

# Run the CLI for development
uv run llmc --help
```

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features. When reporting a bug, include:

- Your operating system and Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Any relevant logs or error messages

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation as needed
3. Ensure your code follows the project's coding standards
4. Submit your pull request with a clear description of the changes
5. Be prepared to respond to feedback and make revisions

## License

By contributing to LLMC, you agree that your contributions will be licensed under the MIT License.