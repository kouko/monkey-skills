// OpenCode v2 plugin loader for philosophers-toolkit
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
        const rawLines = [];
        let j = i + 1;
        // Block scalar: collect lines that are empty or start with whitespace
        while (j < lines.length && (lines[j] === "" || /^\s/.test(lines[j]))) {
          rawLines.push(lines[j]);
          j++;
        }
        const indicator = rest.trimStart()[0]; // '|' or '>'
        const chomping = rest.trimStart()[1] || ''; // '-', '+', or ''
        // Compute common indent of non-empty content lines, strip it from each
        const indents = rawLines
          .filter(l => l.trim().length > 0)
          .map(l => l.length - l.trimStart().length);
        const commonIndent = indents.length > 0 ? Math.min(...indents) : 0;
        const content = rawLines.map(l =>
          l.trim().length > 0 ? l.slice(commonIndent).trimEnd() : ""
        );
        let value;
        if (indicator === "|") {
          // Literal: preserve newlines
          value = content.join("\n");
          // Apply chomping
          if (chomping === "-") {
            value = value.replace(/\n+$/, "");
          } else if (chomping === "+") {
            // '+': keep all trailing newlines; frontmatter delimiter consumed one, add it back
            value += "\n";
          } else {
            // Clip: ensure exactly one trailing newline
            value = value.replace(/\n+$/, "") + "\n";
          }
        } else {
          // Folded: compute common indent, then apply YAML 1.2 folded scalar rules
          const foldedLines = [];
          const len = content.length;
          for (let k = 0; k < len; k++) {
            const line = content[k];
            const isEmpty = line === "";
            const indentMore = !isEmpty && (rawLines[k].length - rawLines[k].trimStart().length > commonIndent);
            if (isEmpty) {
              foldedLines.push("\n");
              continue;
            }
            const text = line;
            // Determine separator before this line
            if (k === 0) {
              // First non-empty line after possible leading blank lines: no prefix
              foldedLines.push(text);
            } else {
              const prev = content[k-1];
              const prevEmpty = prev === "";
              const prevMore = !prevEmpty && (rawLines[k-1].length - rawLines[k-1].trimStart().length > commonIndent);
              if (prevEmpty || prevMore || indentMore) {
                foldedLines.push("\n" + text);
              } else {
                foldedLines.push(" " + text);
              }
            }
          }
          value = foldedLines.join("");
          // Apply chomping for folded
          if (chomping === "-") {
            value = value.replace(/\n+$/, "");
          } else if (chomping === "+") {
            // '+': keep all trailing newlines; frontmatter delimiter consumed one, add it back
            value += "\n";
          } else {
            value = value.replace(/\n+$/, "") + "\n";
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
  id: "monkey-skills-philosophers-toolkit",
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
            id: `monkey-skills-philosophers-toolkit:${entry.name}`,
            name,
            ...(description ? { description } : {}),
            path: skillFile,
            content: skillContent
          });
        } catch (err) {
          console.error(`[monkey-skills-philosophers-toolkit] Failed to load skill ${entry.name}:`, err);
        }
      }

      await ctx.skill.transform((draft) => {
        for (const skill of skills) {
          try {
            draft.add(skill);
          } catch (err) {
            console.error(`[monkey-skills-philosophers-toolkit] Failed to register skill ${skill.id}:`, err);
          }
        }
      });
    } catch (err) {
      console.error(`[monkey-skills-philosophers-toolkit] Loader failed:`, err);
    }
  }
};