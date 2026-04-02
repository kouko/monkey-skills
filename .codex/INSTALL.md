# Installing Monkey Skills for Codex

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kouko/monkey-skills.git ~/.codex/monkey-skills
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/monkey-skills/skills ~/.agents/skills/monkey-skills
   ```

3. **Restart Codex** to discover the skills.

## Updating

```bash
cd ~/.codex/monkey-skills && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/monkey-skills
rm -rf ~/.codex/monkey-skills
```
