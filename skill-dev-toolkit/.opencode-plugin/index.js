// OpenCode v2 plugin loader for skill-dev-toolkit
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
        // | preserves newlines; > folds to spaces
        let value = rest.trimStart()[0] === "|" ? parts.join("\n") : parts.join(" ");
        // Chomping: '-' strips trailing newline(s), default keeps one (clip), '+' keeps all
        if (rest.trimStart()[1] !== "+") {
          value = value.replace(/\s+$/, "");
          if (rest.trimStart()[1] !== "-") {
            value += "\n";
          }
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
  id: "monkey-skills-skill-dev-toolkit",
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
            id: `monkey-skills-skill-dev-toolkit:${entry.name}`,
            name,
            ...(description ? { description } : {}),
            path: skillFile,
            content: skillContent
          });
        } catch (err) {
          console.error(`[monkey-skills-skill-dev-toolkit] Failed to load skill ${entry.name}:`, err);
        }
      }

      await ctx.skill.transform((draft) => {
        for (const skill of skills) {
          try {
            draft.add(skill);
          } catch (err) {
            console.error(`[monkey-skills-skill-dev-toolkit] Failed to register skill ${skill.id}:`, err);
          }
        }
      });
    } catch (err) {
      console.error(`[monkey-skills-skill-dev-toolkit] Loader failed:`, err);
    }
  }
};