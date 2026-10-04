// OpenCode v2 plugin loader for copywriting-toolkit
// Registers all skills in ../skills/ via ctx.skill.transform
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));

// Parse a YAML scalar value (quoted or unquoted) according to YAML 1.2 spec
function parseYAMLScalar(raw) {
  let s = stripYAMLComment(raw.trim());
  // Double-quoted: interpret escape sequences
  if (s.length >= 2 && s[0] === '"' && s[s.length - 1] === '"') {
    return decodeDoubleQuoted(s.slice(1, s.length - 1));
  }
  // Single-quoted: doubled quotes become single quote, no other escapes
  if (s.length >= 2 && s[0] === "'" && s[s.length - 1] === "'") {
    return s.slice(1, s.length - 1).replace(/''/g, "'");
  }
  return s;
}

// Strip a YAML trailing comment: `#` starts a comment when preceded by
// whitespace. Quote-awareness applies only when the scalar itself is quoted
// (a leading quote opens a quoted scalar); quotes inside a plain scalar are
// ordinary characters and do NOT protect a following `#`.
function stripYAMLComment(s) {
  if (s[0] !== '"' && s[0] !== "'") {
    // Plain scalar: first whitespace-preceded `#` starts the comment.
    const idx = s.search(/(^|\s)#/);
    return idx === -1 ? s : s.slice(0, idx).trimEnd();
  }
  let inDQ = false;
  let inSQ = false;
  let escaped = false;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (escaped) { escaped = false; continue; }
    if (inDQ) {
      if (c === "\\") { escaped = true; continue; }
      if (c === '"') inDQ = false;
      continue;
    }
    if (inSQ) {
      if (c === "'" && s[i + 1] === "'") { i++; continue; }
      if (c === "'") inSQ = false;
      continue;
    }
    if (c === '"') { inDQ = true; continue; }
    if (c === "'") { inSQ = true; continue; }
    if (c === '#' && (i === 0 || /\s/.test(s[i - 1]))) {
      return s.slice(0, i).trimEnd();
    }
  }
  return s.trimEnd();
}

// Decode a YAML double-quoted scalar's inner text in one left-to-right pass.
// Covers the full YAML 1.2 escape table; unknown escapes keep the backslash.
function decodeDoubleQuoted(inner) {
  const out = [];
  for (let i = 0; i < inner.length; i++) {
    const c = inner[i];
    if (c !== "\\" || i + 1 >= inner.length) { out.push(c); continue; }
    const e = inner[i + 1];
    const simple = {
      "0": "\u0000", "a": "\u0007", "b": "\u0008", "t": "\u0009",
      "n": "\u000A", "v": "\u000B", "f": "\u000C", "r": "\u000D",
      "e": "\u001B", " ": " ", '"': '"', "/": "/", "\\": "\\",
      "N": "\u0085", "_": "\u00A0", "L": "\u2028", "P": "\u2029"
    };
    if (Object.prototype.hasOwnProperty.call(simple, e)) {
      out.push(simple[e]);
      i += 1;
      continue;
    }
    if (e === "x" && /^[0-9A-Fa-f]{2}$/.test(inner.slice(i + 2, i + 4))) {
      out.push(String.fromCharCode(parseInt(inner.slice(i + 2, i + 4), 16)));
      i += 3;
      continue;
    }
    if (e === "u" && /^[0-9A-Fa-f]{4}$/.test(inner.slice(i + 2, i + 6))) {
      out.push(String.fromCharCode(parseInt(inner.slice(i + 2, i + 6), 16)));
      i += 5;
      continue;
    }
    if (e === "U" && /^[0-9A-Fa-f]{8}$/.test(inner.slice(i + 2, i + 10))) {
      const cp = parseInt(inner.slice(i + 2, i + 10), 16);
      out.push(cp <= 0x10FFFF ? String.fromCodePoint(cp) : "\uFFFD");
      i += 9;
      continue;
    }
    // Unknown escape: preserve the backslash and the next character verbatim.
    out.push("\\" + e);
    i += 1;
  }
  return out.join("");
}

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
      name = parseYAMLScalar(line.slice(5));
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
          l.trim().length > 0 ? l.slice(commonIndent) : ""
        );
        let value;
        if (indicator === "|") {
          // Literal: preserve newlines
          // Empty block scalar (no content lines) -> empty string (all chomping modes)
          if (content.length === 0) {
            value = "";
          } else {
            value = content.join("\n");
            // Apply chomping (compensate for regex consuming the newline before `---`)
            if (chomping === "-") {
              value = value.replace(/\n+$/, "");
            } else if (chomping === "+") {
              // keep: add back the consumed delimiter newline
              value += "\n";
            } else {
              // clip (default): ensure exactly one trailing newline
              value = value.replace(/\n+$/, "") + "\n";
            }
          }
        } else {
          // Folded: apply YAML 1.2 folded scalar rules
          // - Line breaks folded to spaces, except:
          //   * blank line → single newline (paragraph break)
          //   * more-indented line → newline + preserve extra indent
          //   * line after more-indented → newline
          // - chomping: strip (-) / clip (default, strips) / keep (+)
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
            if (k === 0) {
              // First non-empty line
              foldedLines.push(text);
            } else {
              const prev = content[k-1];
              const prevEmpty = prev === "";
              const prevMore = !prevEmpty && (rawLines[k-1].length - rawLines[k-1].trimStart().length > commonIndent);
              if (prevMore || indentMore) {
                foldedLines.push("\n" + text);
              } else {
                // prevEmpty: the blank line already contributed its newline
                foldedLines.push(prevEmpty ? text : " " + text);
              }
            }
          }
          value = foldedLines.join("");
          // Apply chomping for folded (compensate for regex consuming the newline before `---`)
          // Empty block scalar -> empty string (all chomping modes)
          if (content.length === 0) {
            value = "";
          } else if (chomping === "-") {
            value = value.replace(/\n+$/, "");
          } else if (chomping === "+") {
            // keep: add back the consumed delimiter newline
            value += "\n";
          } else {
            // clip (default): ensure exactly one trailing newline
            value = value.replace(/\n+$/, "") + "\n";
          }
        }
        description = value;
        i = j - 1;
      } else {
        description = parseYAMLScalar(rest);
      }
    }
  }
  return { frontmatter: { name, description }, content: raw.slice(m[0].length) };
}

export default {
  id: "monkey-skills-copywriting-toolkit",
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

          // Skill without a description is not advertised (negative acceptance case)
          if (!description) {
            continue;
          }

          skills.push({
            id: `monkey-skills-copywriting-toolkit:${entry.name}`,
            name,
            description,
            path: skillFile,
            content: skillContent
          });
        } catch (err) {
          console.error(`[monkey-skills-copywriting-toolkit] Failed to load skill ${entry.name}:`, err);
        }
      }

      await ctx.skill.transform((draft) => {
        for (const skill of skills) {
          try {
            draft.add(skill);
          } catch (err) {
            console.error(`[monkey-skills-copywriting-toolkit] Failed to register skill ${skill.id}:`, err);
          }
        }
      });
    } catch (err) {
      console.error(`[monkey-skills-copywriting-toolkit] Loader failed:`, err);
    }
  }
};