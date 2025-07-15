# France Chômage CLI - Improvement Report

## Executive Summary

The current CLI implementation in `france_chomage/cli.py` is functional but suffers from code duplication, limited scalability, and suboptimal user experience. This report outlines specific improvements to enhance maintainability, usability, and extensibility.

## Current State Analysis

### Strengths
- ✅ **Functional**: All core operations work correctly
- ✅ **Comprehensive**: Covers all major use cases (scraping, sending, database management)
- ✅ **Modern Framework**: Uses Typer, a modern CLI framework
- ✅ **Async Support**: Properly handles async operations
- ✅ **Documentation**: Good help text for commands

### Pain Points
- ❌ **Code Duplication**: Domain validation logic repeated 4 times
- ❌ **Poor Scalability**: Adding new job categories requires touching multiple places
- ❌ **Inconsistent Output**: Mix of `print()` and `typer.echo()`
- ❌ **Manual Validation**: Custom domain validation instead of leveraging Typer's built-in features
- ❌ **Monolithic Structure**: 291 lines in a single file
- ❌ **No Testing**: CLI commands lack unit tests
- ❌ **Limited UX**: No colors, progress bars, or rich output
- ❌ **Async Boilerplate**: Unnecessary async wrapper functions

## Improvement Recommendations

### 1. Domain Modeling & Data Structure

**Current Issue**: Domain validation is hardcoded in multiple places.

**Solution**: Create a centralized domain model:

```python
from enum import Enum
from typing import Dict, Type

class Domain(str, Enum):
    communication = "communication"
    design = "design"
    restauration = "restauration"

# Centralized mapping
SCRAPERS: Dict[Domain, Type[BaseScraper]] = {
    Domain.communication: CommunicationScraper,
    Domain.design: DesignScraper,
    Domain.restauration: RestaurationScraper,
}

TOPIC_IDS: Dict[Domain, int] = {
    Domain.communication: settings.telegram_communication_topic_id,
    Domain.design: settings.telegram_design_topic_id,
    Domain.restauration: settings.telegram_restauration_topic_id,
}
```

**Benefits**:
- Single source of truth for domains
- Automatic validation via Typer
- Easy to add new categories
- Type safety

### 2. CLI Architecture Restructuring

**Current Issue**: All commands in one file, flat command structure.

**Solution**: Implement sub-applications and modular structure:

```python
# france_chomage/cli/__init__.py
import typer
from .scraping import scrape_app
from .sending import send_app
from .database import db_app
from .utils import utils_app

app = typer.Typer(
    help="🇫🇷 France Chômage Bot",
    rich_markup_mode="rich",
    asyncio_mode="auto"
)

app.add_typer(scrape_app, name="scrape")
app.add_typer(send_app, name="send")
app.add_typer(db_app, name="db")
app.add_typer(utils_app, name="utils")
```

**New Command Structure**:
```bash
france_chomage scrape [domain]          # Instead of: france_chomage scrape [domain]
france_chomage send [domain]            # Instead of: france_chomage send [domain]
france_chomage db init                   # Instead of: france_chomage db-init
france_chomage db migrate                # Instead of: france_chomage db-migrate
france_chomage db status                 # Instead of: france_chomage db-status
france_chomage db cleanup [--days=90]   # Instead of: france_chomage db-cleanup
france_chomage utils info                # Instead of: france_chomage info
france_chomage utils test                # Instead of: france_chomage test
```

### 3. Remove Async Boilerplate

**Current Issue**: Every command has inner async function + `asyncio.run()`.

**Solution**: Use Typer's built-in async support:

```python
# Before
@app.command()
def scrape(domain: str):
    async def _scrape():
        # logic here
    asyncio.run(_scrape())

# After
@scrape_app.command()
async def once(domain: Domain):
    scraper = SCRAPERS[domain]()
    jobs = await scraper.scrape()
    typer.secho(f"✅ {len(jobs)} jobs scraped", fg="green")
```

### 4. Enhanced User Experience

**Current Issue**: Basic text output, no colors, no progress indication.

**Solution**: Implement rich output with progress bars:

```python
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

console = Console()

@scrape_app.command()
async def once(domain: Domain):
    with Progress() as progress:
        task = progress.add_task(f"Scraping {domain}...", total=None)
        scraper = SCRAPERS[domain]()
        jobs = await scraper.scrape()
        progress.update(task, completed=True)
    
    # Display results in a table
    table = Table(title=f"Scraping Results - {domain.title()}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Jobs Found", str(len(jobs)))
    table.add_row("Status", "✅ Success")
    console.print(table)
```

### 5. Comprehensive Error Handling

**Current Issue**: Basic error handling, limited debugging information.

**Solution**: Implement structured error handling:

```python
import logging
from rich.traceback import install
from rich.logging import RichHandler

# Install rich traceback handler
install(show_locals=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)
```

### 6. Configuration Management

**Current Issue**: Settings accessed directly throughout CLI.

**Solution**: Create configuration utilities:

```python
# france_chomage/cli/config.py
import typer
from rich.table import Table
from ..config import settings

config_app = typer.Typer(help="Configuration management")

@config_app.command("show")
def show_config():
    """Display current configuration"""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Location", settings.location)
    table.add_row("Results Wanted", str(settings.results_wanted))
    table.add_row("Communication Topic", str(settings.telegram_communication_topic_id))
    # ... more settings
    
    console.print(table)

@config_app.command("validate")
async def validate_config():
    """Validate configuration and test connections"""
    # Test database connection
    # Test Telegram connection
    # Validate environment variables
```

### 7. Testing Infrastructure

**Current Issue**: No CLI tests.

**Solution**: Implement comprehensive CLI testing:

```python
# france_chomage/tests/test_cli.py
from typer.testing import CliRunner
from france_chomage.cli import app

runner = CliRunner()

def test_scrape_command():
    result = runner.invoke(app, ["scrape", "communication"])
    assert result.exit_code == 0
    assert "jobs scraped" in result.stdout

def test_invalid_domain():
    result = runner.invoke(app, ["scrape", "invalid"])
    assert result.exit_code == 2  # Typer's validation error

def test_db_status():
    result = runner.invoke(app, ["db", "status"])
    assert result.exit_code == 0
```

### 8. Advanced Features

**New Features to Add**:

1. **Dry Run Mode**:
   ```bash
   france_chomage send communication --dry-run
   ```

2. **Configuration Generator**:
   ```bash
   france_chomage config create-template
   ```

3. **Shell Completion**:
   ```bash
   france_chomage --install-completion
   ```

4. **Version Information**:
   ```bash
   france_chomage --version
   ```

5. **Batch Operations**:
   ```bash
   france_chomage scrape all
   france_chomage workflow all
   ```

## Implementation Priority

### Phase 1: Core Refactoring (High Priority)
1. Create domain enum and centralized mappings
2. Implement sub-applications structure
3. Remove async boilerplate
4. Add basic error handling

### Phase 2: Enhanced UX (Medium Priority)
1. Implement rich output with colors and tables
2. Add progress indicators
3. Improve error messages
4. Add global flags (--verbose, --quiet)

### Phase 3: Advanced Features (Low Priority)
1. Add CLI testing
2. Implement dry-run mode
3. Add shell completion
4. Create configuration utilities

## Expected Benefits

### For Developers
- **Reduced Maintenance**: 40% less code duplication
- **Easier Testing**: Modular structure enables unit testing
- **Better Debugging**: Rich tracebacks and logging
- **Faster Development**: Adding new categories requires minimal changes

### For Users
- **Better UX**: Rich output, progress bars, colored text
- **Clearer Errors**: Better error messages and debugging info
- **More Discoverable**: Grouped commands and better help
- **More Reliable**: Comprehensive validation and error handling

## File Structure After Refactoring

```
france_chomage/
├── cli/
│   ├── __init__.py       # Main app and sub-app registration
│   ├── scraping.py       # Scraping commands
│   ├── sending.py        # Telegram sending commands
│   ├── database.py       # Database management commands
│   ├── config.py         # Configuration utilities
│   ├── utils.py          # Utility commands (info, test, etc.)
│   └── shared.py         # Shared types and utilities
├── tests/
│   ├── test_cli.py       # CLI tests
│   └── ...
└── ...
```

## Conclusion

These improvements will transform the CLI from a functional but maintenance-heavy tool into a modern, scalable, and user-friendly interface. The modular architecture will make it easier to add new features and job categories while providing a better experience for both developers and end users.

The implementation can be done incrementally, starting with the core refactoring and gradually adding enhanced features. Each phase delivers immediate value while building toward a more robust and maintainable CLI system.
