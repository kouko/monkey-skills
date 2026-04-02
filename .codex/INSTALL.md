# Installing Monkey Skills for Codex

## Prerequisites

- Git

## Option A: Install as skills (standalone)

```bash
git clone https://github.com/kouko/monkey-skills.git ~/.codex/monkey-skills

mkdir -p ~/.agents/skills
ln -s ~/.codex/monkey-skills/skills ~/.agents/skills/monkey-skills
```

## Option B: Install as plugin

```bash
git clone https://github.com/kouko/monkey-skills.git ~/.codex/plugins/monkey-skills
```

Restart Codex to discover the skills.

## Updating

```bash
cd ~/.codex/monkey-skills && git pull
# or
cd ~/.codex/plugins/monkey-skills && git pull
```

## Uninstalling

```bash
# Option A
rm ~/.agents/skills/monkey-skills
rm -r ~/.codex/monkey-skills

# Option B
rm -r ~/.codex/plugins/monkey-skills
```
