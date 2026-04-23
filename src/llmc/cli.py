import os
import re
import requests
import shutil
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import litellm

from llmc.services.provider_services import ProviderServices
from llmc.services.ai_model_services import AIModelServices
from llmc.services.sync_service import SyncService, Agents
from llmc.models import AIModel

def ensure_config_files():
    """Ensure agents.json and providers.json exist in local config."""
    config_dir = Path.home() / ".config/aimodels"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Resolve the path to the seeds directory relative to this file's location
    # src/llmc/cli.py -> src/llmc/ -> src/ -> project_root/
    current_file_dir = Path(__file__).resolve().parent.parent.parent
    seeds_dir = current_file_dir / "seeds"

    for filename in ["agents.json", "providers.json"]:
        dest = config_dir / filename
        if not dest.exists():
            src = seeds_dir / filename
            if src.exists():
                shutil.copy(src, dest)

app = typer.Typer(no_args_is_help=True)
console = Console()

providers_app = typer.Typer()
models_app = typer.Typer()
agents_app = typer.Typer()
ensure_config_files()


def get_local_models(provider) -> list[str]:
    """Get models from local/OpenAI-compatible server like Ollama."""
    base_url = provider.connection.base_url.rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-2]
    elif "/v1" not in base_url:
        base_url = base_url + "/v1"

    try:
        response = requests.get(f"{base_url}/models", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
    except Exception:
        pass

    try:
        base_url = provider.connection.base_url.rstrip("/")
        if base_url.endswith("/v1"):
            base_url = base_url[:-3]
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass

    return []


def get_openrouter_models(api_key: str) -> list[str]:
    """Get models from OpenRouter API directly."""
    if not api_key:
        return []

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models", headers=headers, timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
    except Exception:
        pass

    return []


def get_api_key_status(provider, model_name: str = None) -> str:
    """Check if API key is required/available for provider and optional model."""
    api_key = provider.connection.api_key or ""

    # Check if key is in keyring - get actual key to verify it's available
    if provider.connection.api_key_in_keyring:
        from llmc.services.keyring_service import KeyringService
        api_key = KeyringService.get_key(provider.id) or ""

    # Check if this is a local provider (Ollama or OpenAI-compatible)
    is_local = (
        provider.provider_type == "ollama"
        or "localhost" in provider.connection.base_url
        or "127.0.0.1" in provider.connection.base_url
    )

    # For local providers like Ollama
    if is_local:
        # Check model-specific requirements (cloud/deployed models need API key)
        if model_name:
            name_lower = model_name.lower()
            if ":cloud" in name_lower or "-cloud" in name_lower:
                # If key exists and is valid, return ✓
                if api_key and api_key not in ("", "ollama", "none", "na", "no", "null", "n/a"):
                    return "✓"
                return "?"
        return "✗"

    # For cloud providers
    # Check if placeholder ${VAR}
    if api_key.startswith("${") and api_key.endswith("}"):
        return "?"

    # Check for empty/no key
    no_key_values = {"", "ollama", "none", "na", "no", "null", "n/a"}
    if api_key.lower() in no_key_values:
        return "?"

    # Valid key provided
    return "✓"


@providers_app.command("list")
def providers_list():
    """List all providers"""
    ps = ProviderServices()
    ps.refresh()
    providers = ps.get_all(resolve_keys=False)

    table = Table(title="Providers")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Enabled", style="magenta")
    table.add_column("Base URL")
    table.add_column("Key", style="cyan")

    for p in providers:
        key_status = "<stored>" if p.connection.api_key_in_keyring else ("*" if p.connection.api_key else "")
        table.add_row(
            p.id,
            p.name,
            p.provider_type,
            "✓" if p.enabled else "✗",
            p.connection.base_url,
            key_status,
        )

    console.print(table)


@providers_app.command("get")
def providers_get(provider_id: str):
    """Get a provider by ID (API key is masked)"""
    ps = ProviderServices()
    ps.refresh()
    provider = ps.get_by_id(provider_id, resolve_key=False)

    if provider is None:
        console.print(f"[red]Provider '{provider_id}' not found[/red]")
        raise typer.Exit(code=1)

    data = provider.model_dump(mode='json')

    if data.get('connection', {}).get('api_key_in_keyring'):
        data['connection']['api_key'] = "<stored>"
    elif data.get('connection', {}).get('api_key'):
        data['connection']['api_key'] = "<redacted>"

    console.print(data)


@providers_app.command("enable")
def providers_enable(provider_ids: list[str] = typer.Argument(..., help="Provider ID(s) to enable")):
    """Enable one or more providers"""
    ps = ProviderServices()
    ps.refresh()

    enabled = []
    not_found = []

    for provider_id in provider_ids:
        provider = ps.get_by_id(provider_id)
        if provider is None:
            not_found.append(provider_id)
            continue

        provider.enabled = True
        ps.update(provider_id, provider)
        enabled.append(provider_id)

    if not_found:
        console.print(f"[red]Not found: {', '.join(not_found)}[/red]")

    if enabled:
        ps._save()
        console.print(f"[green]Enabled: {', '.join(enabled)}[/green]")


@providers_app.command("disable")
def providers_disable(provider_ids: list[str] = typer.Argument(..., help="Disable one or more providers")):
    """Disable one or more providers"""
    ps = ProviderServices()
    ps.refresh()

    disabled = []
    not_found = []

    for provider_id in provider_ids:
        provider = ps.get_by_id(provider_id)
        if provider is None:
            not_found.append(provider_id)
            continue

        provider.enabled = False
        ps.update(provider_id, provider)
        disabled.append(provider_id)

    if not_found:
        console.print(f"[red]Not found: {', '.join(not_found)}[/red]")

    if disabled:
        ps._save()
        console.print(f"[yellow]Disabled: {', '.join(disabled)}[/yellow]")


@providers_app.command("apikey")
def providers_apikey(
    provider_id: str,
    key: str = typer.Option(None, "-k", "--key", help="API key (will prompt if not provided)"),
    remove: bool = typer.Option(False, "--remove", help="Remove API key from keyring"),
):
    """Add, update, or remove API key for provider (stored in system keyring)"""
    ps = ProviderServices()
    ps.refresh()

    provider = ps.get_by_id(provider_id, resolve_key=False)
    if provider is None:
        console.print(f"[red]Provider '{provider_id}' not found[/red]")
        raise typer.Exit(code=1)

    if remove:
        ps.remove_api_key(provider_id)
        console.print(f"[yellow]API key removed for '{provider_id}'[/yellow]")
        return

    if key is None:
        key = typer.prompt("Enter API key", hide_input=True)

    ps.set_api_key(provider_id, key)
    console.print(f"[green]API key stored for '{provider_id}'[/green]")


@models_app.command("list")
def models_list():
    """List all AI models"""
    ms = AIModelServices()
    ms.refresh()
    models = ms.get_all()

    # Sort by provider_id, then model_name
    models.sort(key=lambda m: (m.provider_id, m.model_name))

    table = Table(title="AI Models")
    table.add_column("ID", style="cyan")
    table.add_column("Model Name", style="green")
    table.add_column("Provider ID", style="yellow")
    table.add_column("Enabled", style="magenta")

    for m in models:
        table.add_row(
            m.id,
            m.model_name,
            m.provider_id,
            "✓" if m.enabled else "✗",
        )

    console.print(table)


@models_app.command("add")
def models_add(
    filter_text: str = typer.Argument(None, help="Filter models (shows interactive list)"),
    provider_id: str = typer.Option(None, "-p", "--provider", help="Provider ID"),
    model: str = typer.Option(None, "-m", "--model", help="Model ID to add (exact match)"),
):
    """Add AI model(s) from candidates. Use filter to show interactive list."""
    ps = ProviderServices()
    ps.refresh()
    ms = AIModelServices()
    ms.refresh()

    # Get enabled providers
    enabled_providers = [p for p in ps.get_all(resolve_keys=False) if p.enabled]

    if not enabled_providers:
        console.print("[red]No enabled providers to add models from[/red]")
        raise typer.Exit(code=1)

    # If provider is specified, filter to that provider
    if provider_id:
        enabled_providers = [p for p in enabled_providers if p.id == provider_id]
        if not enabled_providers:
            console.print(f"[red]Provider '{provider_id}' not found or disabled[/red]")
            raise typer.Exit(code=1)

    # Get candidates for each enabled provider
    all_candidates = []
    for provider in enabled_providers:
        try:
            candidates = get_candidates_for_provider(provider)
            all_candidates.extend([(provider.id, provider.name, m) for m in candidates])
        except Exception as e:
            console.print(f"[yellow]Skipping {provider.name}: {e}[/yellow]")

    if not all_candidates:
        console.print("[yellow]No candidates found[/yellow]")
        return

    # Exclude models that already exist in the models file
    all_candidates = [(pid, pname, m) for pid, pname, m in all_candidates if not ms.get_by_id(m)]

    if not all_candidates:
        console.print("[yellow]All available models already exist in your models list[/yellow]")
        return

    # Sort by provider name, then model name
    all_candidates.sort(key=lambda x: (x[1], x[2]))

    # If model filter (-m) is specified, show matching with confirmation
    if model:
        all_candidates = [(pid, pname, m) for pid, pname, m in all_candidates if model.lower() in m.lower()]

        if not all_candidates:
            console.print(f"[yellow]No models found matching '{model}'[/yellow]")
            return

        # Show matching models
        console.print(f"\n[bold]Matching models:[/bold]")
        table = Table(show_header=False)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Provider", style="yellow")
        table.add_column("Model", style="green")

        for i, (pid, pname, mname) in enumerate(all_candidates):
            table.add_row(str(i + 1), pid, mname)

        console.print(table)
        console.print("")

        if len(all_candidates) == 1:
            confirm = "y"
        else:
            confirm = Prompt.ask(
                f"Add all {len(all_candidates)} models?",
                choices=["y", "n", "yes", "no"],
                default="n",
            )

        if confirm.lower() in ("n", "no"):
            console.print("[yellow]Cancelled[/yellow]")
            return

        added = 0
        for pid, pname, mname in all_candidates:
            new_model = AIModel(
                id=mname,
                model_name=mname,
                provider_id=pid,
                enabled=True,
                metadata={"modalities": ["text"]},
                parameters={},
                cost_per_1m_tokens={"input": 0.0, "output": 0.0},
            )
            ms.create(new_model)
            added += 1

        ms._save()
        console.print(f"\n[green]Added {added} model(s)[/green]")
        return

    # If positional filter is provided, show matching models with confirmation
    if filter_text:
        filtered = [(pid, pname, m) for pid, pname, m in all_candidates if filter_text.lower() in m.lower()]

        if not filtered:
            console.print(f"[yellow]No models found matching '{filter_text}'[/yellow]")
            return

        console.print(f"\n[bold]Matching models:[/bold]")
        table = Table(show_header=False)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Provider", style="yellow")
        table.add_column("Model", style="green")

        for i, (pid, pname, mname) in enumerate(filtered):
            table.add_row(str(i + 1), pid, mname)

        console.print(table)
        console.print("")

        # Ask to add one or all
        choice = Prompt.ask(
            f"Enter number to add (or 'all' to add all {len(filtered)}, 'q' to quit)",
            choices=[str(i + 1) for i in range(len(filtered))] + ["all", "q"],
            default="q",
        )

        if choice.lower() == "q":
            console.print("[yellow]Cancelled[/yellow]")
            return

        if choice.lower() == "all":
            to_add = filtered
        else:
            idx = int(choice) - 1
            to_add = [filtered[idx]]

        for pid, pname, mname in to_add:
            new_model = AIModel(
                id=mname,
                model_name=mname,
                provider_id=pid,
                enabled=True,
                metadata={"modalities": ["text"]},
                parameters={},
                cost_per_1m_tokens={"input": 0.0, "output": 0.0},
            )
            ms.create(new_model)

        ms._save()
        console.print(f"[green]Added {len(to_add)} model(s)[/green]")
        return

    # No filter - show interactive table selection

    table = Table(title="Available Models", show_header=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="green")

    for i, (pid, pname, mname) in enumerate(all_candidates):
        exists = "[dim](exists)[/dim]" if ms.get_by_id(mname) else ""
        table.add_row(str(i + 1), pid, f"{mname} {exists}")

    console.print(table)
    console.print("")

    # Prompt for selection
    selected = Prompt.ask(
        "Enter number to add (or 'q' to quit)",
        choices=[str(i + 1) for i in range(len(all_candidates))] + ["q"],
        default="q",
    )

    if selected.lower() == "q":
        console.print("[yellow]Cancelled[/yellow]")
        return

    try:
        idx = int(selected) - 1
        if idx < 0 or idx >= len(all_candidates):
            console.print("[red]Invalid selection[/red]")
            raise typer.Exit(code=1)
        pid, pname, mname = all_candidates[idx]
    except ValueError:
        console.print("[red]Invalid selection[/red]")
        raise typer.Exit(code=1)

    # Check if already exists
    if ms.get_by_id(mname):
        console.print(f"[yellow]Model '{mname}' already exists[/yellow]")
        return

    # Add the model
    new_model = AIModel(
        id=mname,
        model_name=mname,
        provider_id=pid,
        enabled=True,
        metadata={"modalities": ["text"]},
        parameters={},
        cost_per_1m_tokens={"input": 0.0, "output": 0.0},
    )
    ms.create(new_model)
    ms._save()
    console.print(f"[green]Added '{mname}' from {pname}[/green]")


def get_candidates_for_provider(provider):
    """Get model candidates from a provider."""
    api_key = provider.connection.api_key or ""
    if api_key and api_key.startswith("${") and api_key.endswith("}"):
        env_var = api_key[2:-1]
        api_key = os.environ.get(env_var)

    if not api_key or api_key == "ollama":
        api_key = None

    # Check if this is a local provider
    is_local = (
        provider.provider_type == "ollama"
        or "localhost" in provider.connection.base_url
        or "127.0.0.1" in provider.connection.base_url
    )

    if is_local:
        return get_local_models(provider)
    elif provider.provider_type == "openrouter":
        if provider.connection.api_key_in_keyring:
            from llmc.services.keyring_service import KeyringService
            api_key = KeyringService.get_key(provider.id)
        return get_openrouter_models(api_key)
    else:
        if provider.connection.api_key_in_keyring:
            from llmc.services.keyring_service import KeyringService
            api_key = KeyringService.get_key(provider.id)
        return litellm.get_valid_models(
            custom_llm_provider=provider.provider_type,
            api_key=api_key,
            api_base=provider.connection.base_url,
        )


@models_app.command("get")
def models_get(model_id: str):
    """Get an AI model by ID"""
    ms = AIModelServices()
    ms.refresh()
    model = ms.get_by_id(model_id)

    if model is None:
        console.print(f"[red]Model '{model_id}' not found[/red]")
        raise typer.Exit(code=1)

    console.print(model.model_dump_json(indent=2))


@agents_app.command("sync")
def agents_sync(
    agent_ids: str = typer.Option(None, "-a", "--agent", help="Agent ID(s) to sync (comma-separated)"),
    model_filter: str = typer.Option(None, "-m", "--model", help="Filter models by name"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be changed without applying"),
):
    """Sync selected models to coding agent configs"""
    ps = ProviderServices()
    ps.refresh()
    ms = AIModelServices()
    ms.refresh()

    available_models = ms.get_all()
    if not available_models:
        console.print("[yellow]No models in your models.json - add some first[/yellow]")
        return

    if model_filter:
        available_models = [m for m in available_models if model_filter.lower() in m.model_name.lower()]

    ss = SyncService()
    agents = ss.discover()

    if not agents:
        console.print("[yellow]No agents configured - run 'llmc agents discover' first[/yellow]")
        return

    existing = [a for a in agents if a.get("exists")]
    missing = [a for a in agents if not a.get("exists")]

    if missing:
        console.print("[yellow]Missing configs (skipped):[/yellow]")
        for a in missing:
            console.print(f"  {a['name']}: {a['config_path']}")

    if not existing:
        console.print("[yellow]No agent configs found on this system[/yellow]")
        return

    table = Table(title="Available Agents")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Agent", style="green")
    table.add_column("Config", style="yellow")

    for i, a in enumerate(existing):
        multi = "[multi]" if a.get("supports_multiple") else ""
        table.add_row(str(i + 1), f"{a['name']} {multi}", a["config_path"])

    console.print(table)

    if agent_ids:
        selected_ids = [aid.strip() for aid in agent_ids.split(",")]
    else:
        console.print("")
        selected = Prompt.ask(
            "Enter agent numbers (comma-separated, 'all', or 'q' to quit)",
            default="q",
        )
        if selected.lower() == "q":
            console.print("[yellow]Cancelled[/yellow]")
            return

        if selected.lower() == "all":
            selected_ids = [a["id"] for a in existing]
        else:
            indices = [int(i.strip()) - 1 for i in selected.split(",") if i.strip().isdigit()]
            selected_ids = [existing[i]["id"] for i in indices if 0 <= i < len(existing)]

    selected_agents = [a for a in existing if a["id"] in selected_ids]

    if not selected_agents:
        console.print("[red]No agents selected[/red]")
        return

    console.print(f"\n[bold]Selected agents:[/bold]")
    for a in selected_agents:
        console.print(f"  - {a['name']}")

    console.print(f"\n[bold]Available models ({len(available_models)}):[/bold]")
    for m in available_models:
        console.print(f"  - {m.id} ({m.provider_id})")

    console.print("")

    confirm = Prompt.ask(
        "Sync these models to selected agents?",
        choices=["y", "n", "yes", "no"],
        default="n",
    )

    if confirm.lower() in ("n", "no"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    results = []
    for a in selected_agents:
        result = ss.apply_sync(a["id"], available_models, dry_run=dry_run)
        results.append(result)

    for r in results:
        if "error" in r:
            console.print(f"[red]{r['agent']}: {r['error']}[/red]")
        elif dry_run:
            console.print(f"[cyan]{r['agent']}:[/cyan] dry run - no changes made")
        else:
            console.print(f"[green]{r['agent']}: synced {len(r.get('models_synced', []))} model(s)[/green]")
            if r.get("backup"):
                console.print(f"  backup: {r['backup']}")


@agents_app.command("list")
def agents_list():
    """List configured agents"""
    agents = Agents.load()

    if not agents.agents:
        console.print("[yellow]No agents configured[/yellow]")
        console.print("Run 'llmc agents discover' to find agents on your system")
        return

    table = Table(title="Agents")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="yellow")
    table.add_column("Config Path")
    table.add_column("Exists", style="magenta")

    for a in agents.list_all():
        table.add_row(a.id, a.name, a.description, a.config_path, "✓" if a.exists() else "✗")

    console.print(table)


@agents_app.command("discover")
def agents_discover():
    """Discover coding agents on your system and update agents.json"""
    import os
    from pathlib import Path

    known_agents = [
        {
            "id": "opencode",
            "name": "OpenCode",
            "description": "OpenCode AI CLI assistant",
            "config_path": "~/.config/opencode/opencode.json",
            "model_field": "provider",
            "supports_multiple": True,
            "model_format": "opencode",
        },
        {
            "id": "aider",
            "name": "Aider",
            "description": "AI pair programmer in terminal",
            "config_path": "~/.aider.conf.yml",
            "model_field": "model",
            "supports_multiple": False,
            "model_format": "aider",
        },
        {
            "id": "claude",
            "name": "Claude",
            "description": "Anthropic's Claude Code CLI",
            "config_path": "~/.claude/settings.json",
            "model_field": "model",
            "supports_multiple": False,
            "model_format": "claude",
        },
        {
            "id": "hermes",
            "name": "Hermes",
            "description": "Custom coding agent framework",
            "config_path": "~/.hermes/config.yaml",
            "model_field": "models",
            "supports_multiple": True,
            "model_format": "hermes",
        },
        {
            "id": "pi",
            "name": "PI",
            "description": "PI coding agent",
            "config_path": "~/.pi/config.json",
            "model_field": "default_model",
            "supports_multiple": False,
            "model_format": "pi",
        },
    ]

    found = []
    for agent in known_agents:
        path = Path(os.path.expanduser(agent["config_path"]))
        if path.exists():
            found.append(agent)
            console.print(f"[green]✓[/green] Found: {agent['name']} ({agent['config_path']})")
        else:
            console.print(f"[dim]✗[/dim] Not found: {agent['name']} ({agent['config_path']})")

    if not found:
        console.print("[yellow]No agents found on this system[/yellow]")
        return

    console.print("")
    confirm = Prompt.ask(
        f"Save {len(found)} agent(s) to agents.json?",
        choices=["y", "n", "yes", "no"],
        default="y",
    )

    if confirm.lower() in ("n", "no"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    agents_obj = Agents.load()
    existing_ids = {a.id for a in agents_obj.list_all()}

    for agent in found:
        if agent["id"] not in existing_ids:
            from llmc.services.sync_service import Agent

            agents_obj.agents.append(
                Agent(
                    id=agent["id"],
                    name=agent["name"],
                    description=agent["description"],
                    config_path=agent["config_path"],
                    model_field=agent["model_field"],
                    supports_multiple=agent["supports_multiple"],
                    model_format=agent["model_format"],
                )
            )

    agents_obj.save()
    console.print(f"[green]Saved {len(agents_obj.list_all())} agent(s) to agents.json[/green]")


app.add_typer(providers_app, name="providers")
app.add_typer(models_app, name="models")
app.add_typer(agents_app, name="agents")


@app.command()
def candidates(
    provider_id: str = typer.Option(None, "-p", "--provider", help="Provider ID"),
    filter_text: str = typer.Argument(None, help="Filter models by name"),
):
    """List available models from enabled providers"""
    ps = ProviderServices()
    ps.refresh()

    if provider_id:
        providers = [ps.get_by_id(provider_id)]
        if providers[0] is None:
            console.print(f"[red]Provider '{provider_id}' not found[/red]")
            raise typer.Exit(code=1)
        if not providers[0].enabled:
            console.print(f"[yellow]Provider '{provider_id}' is disabled[/yellow]")
            return
    else:
        providers = [p for p in ps.get_all() if p.enabled]

    if not providers:
        console.print("[yellow]No enabled providers to query[/yellow]")
        return

    table = Table(title="Available Models")
    table.add_column("Provider", style="cyan")
    table.add_column("Model ID", style="green")
    table.add_column("Auth", style="yellow")

    total_models = 0

    for provider in providers:
        api_key = provider.connection.api_key
        if api_key and api_key.startswith("${") and api_key.endswith("}"):
            env_var = api_key[2:-1]
            api_key = os.environ.get(env_var)

        if not api_key or api_key == "ollama":
            api_key = None

        try:
            is_local = (
                provider.provider_type == "ollama"
                or "localhost" in provider.connection.base_url
                or "127.0.0.1" in provider.connection.base_url
            )

            if is_local:
                models = get_local_models(provider)
            elif provider.provider_type == "openrouter":
                models = get_openrouter_models(api_key)
            else:
                models = litellm.get_valid_models(
                    custom_llm_provider=provider.provider_type,
                    api_key=api_key,
                    api_base=provider.connection.base_url,
                )

            if filter_text:
                models = [m for m in models if filter_text.lower() in m.lower()]

            for model in models:
                auth_status = get_api_key_status(provider, model)
                table.add_row(provider.name, model, auth_status)

            total_models += len(models)
        except Exception as e:
            console.print(f"[red]Error querying {provider.name}: {e}[/red]")

    if total_models == 0:
        console.print("[yellow]No models found[/yellow]")
    else:
        console.print(table)


if __name__ == "__main__":
    ensure_config_files()
    app()
