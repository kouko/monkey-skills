// OpenCode v2 plugin loader for gws-toolkit
// Registers all skills in ../skills/ via ctx.skill.transform
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));

function extractFrontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { frontmatter: {}, content: raw };
  const fm = m[1];
  let name;
  let description;
  const lines = fm.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("name:")) {
      name = line.slice(5).trim();
    } else if (line.startsWith("description:")) {
      const rest = line.slice("description:".length);
      // YAML block scalar indicator: | > |- |+ >- >+ — value continues on indented lines
      if (/^\s*[|>][-+]?/.test(rest)) {
        const parts = [];
        let j = i + 1;
        while (j < lines.length && /^\s/.test(lines[j])) {
          parts.push(lines[j].replace(/^\s+/, "").trimEnd());
          j++;
        }
        // Determine block scalar style
        const indicator = rest.trimStart()[0]; // '|' or '>'
        const chomping = rest.trimStart()[1] || ''; // '-', '+', or ''
        let value = '';
        if (indicator === '|') {
          // literal: preserve newlines
          value = parts.join('\n');
          // apply chomping
          if (chomping === '-') {
            // strip trailing newlines
            value = value.replace(/\n+$/, '');
          } else if (chomping === '+') {
            // keep trailing newlines (and ensure at least one trailing newline? per spec, |+ means keep trailing newlines and also add for empty lines? we'll just keep)
            // Actually we already have the newlines from join, so we keep them.
            // But we need to ensure there is a trailing newline if the original had? We'll just keep as is.
          } else {
            // no chomping indicator: keep trailing newlines (default)
            // Actually per spec, | without indicator is same as |+? We'll keep trailing newlines.
            // We'll do nothing.
          }
        } else if (indicator === '>') {
          // folded: replace newlines with spaces, except empty lines
          // First, fold lines: each line trimmed, then join by space
          const folded = parts.map(p => p.trim()).filter(p => p.length > 0).join(' ');
          value = folded;
          // For folded scalars, chomping works similarly? Actually chomping indicator affects trailing newlines as well.
          // We'll ignore for now because corpus has no interior blank lines and likely no chomping on > except >-.
          // We'll handle chomping for folded as well:
          if (chomping === '-') {
            // strip trailing newlines (but folded scalar usually doesn't have trailing newlines unless there are empty lines)
            value = value.replace(/\n+$/, '');
          } else if (chomping === '+') {
            // keep trailing newlines
            // We'll add a trailing newline if the original had? We'll just keep as is.
          } else {
            // no chomping: strip trailing newlines (default for >)
            value = value.replace(/\n+$/, '');
          }
        } else {
          // fallback to old behavior
          value = parts.filter(Boolean).join(" ");
        }
        description = value;
        i = j - 1;
      } else {
        description = rest.trim();
        if ((description.startsWith("\"") && description.endsWith("\"")) ||
            (description.startsWith("'") && description.endsWith("'"))) {
          description = description.slice(1, -1);
        }
      }
    }
  }
  return { frontmatter: { name, description }, content: raw.slice(m[0].length) };
}

export default {
  id: "monkey-skills-gws-toolkit",
  async setup(ctx) {
    try {
      const skillsPath = join(dirname(dirname(fileURLToPath(import.meta.url))), "skills");

      // Check if skills directory exists and is a directory
      if (!existsSync(skillsPath) || !statSync(skillsPath).isDirectory()) {
        return;
      }

      const skills = [];
      const entries = readdirSync(skillsPath, { withFileTypes: true });

      for (const entry of entries) {
        if (!entry.isDirectory() || entry.name.startsWith(".")) {
          continue;
        }

        const skillDir = join(skillsPath, entry.name);
        const skillFile = join(skillDir, "SKILL.md");

        try {
          if (!statSync(skillFile).isFile()) {
            continue;
          }

          const content = readFileSync(skillFile, "utf8");
          const { frontmatter, content: skillContent } = extractFrontmatter(content);
          const name = frontmatter.name || entry.name;
          const description = frontmatter.description;

          skills.push({
            id: `monkey-skills-gws-toolkit:${entry.name}`,
            name,
            ...(description ? { description } : {}),
            path: skillFile,
            content: skillContent
          });
        } catch (err) {
          console.error(`[monkey-skills-gws-toolkit] Failed to load skill ${entry.name}:`, err);
        }
      }

      await ctx.skill.transform((draft) => {
        for (const skill of skills) {
          try {
            draft.add(skill);
          } catch (err) {
            console.error(`[monkey-skills-gws-toolkit] Failed to register skill ${skill.id}:`, err);
          }
        }
      });
    } catch (err) {
      console.error(`[monkey-skills-gws-toolkit] Loader failed:`, err);
    }
  }
};