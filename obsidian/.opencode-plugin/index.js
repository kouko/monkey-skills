export default {
  id: "monkey-skills-obsidian",
  async setup(ctx) {
    try {
      const { dirname, join } = await import('path');
      const { fileURLToPath } = await import('url');
      const { readFileSync, readdirSync, statSync } = await import('fs');

      const __filename = fileURLToPath(import.meta.url);
      const __dirname = dirname(__filename);
      const skillsPath = join(dirname(dirname(__filename)), 'skills');

      if (!statSync(skillsPath).isDirectory()) {
        return;
      }

      const skills = [];
      const entries = readdirSync(skillsPath, { withFileTypes: true });

      for (const entry of entries) {
        if (!entry.isDirectory() || entry.name.startsWith('.')) {
          continue;
        }

        const skillDir = join(skillsPath, entry.name);
        const skillFile = join(skillDir, 'SKILL.md');

        try {
          if (!statSync(skillFile).isFile()) {
            continue;
          }

          const content = readFileSync(skillFile, 'utf8');
          const frontmatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
          let name = entry.name;
          let description = undefined;
          let skillContent = content;

          if (frontmatterMatch) {
            const frontmatter = frontmatterMatch[1];
            const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
            if (nameMatch) {
              name = nameMatch[1].trim();
            }
            // Only capture single-line description values (not multi-line YAML literals)
            const descMatch = frontmatter.match(/^description:\s*(.+)$/m);
            if (descMatch) {
              const descValue = descMatch[1].trim();
              // Only use description if it's not a YAML literal block scalar (| or >)
              if (!descValue.startsWith('|') && !descValue.startsWith('>')) {
                description = descValue;
              }
            }
            skillContent = content.substring(frontmatterMatch.index + frontmatterMatch[0].length);
          }

          skills.push({
            id: `monkey-skills-obsidian:${entry.name}`,
            name,
            ...(description ? { description } : {}),
            path: skillFile,
            content: skillContent
          });
        } catch (err) {
          console.error(`[monkey-skills-obsidian] Failed to load skill ${entry.name}:`, err);
        }
      }

      ctx.skill.transform((draft) => {
        for (const skill of skills) {
          try {
            draft.add(skill);
          } catch (err) {
            console.error(`[monkey-skills-obsidian] Failed to register skill ${skill.id}:`, err);
          }
        }
      });
    } catch (err) {
      console.error(`[monkey-skills-obsidian] Loader failed:`, err);
    }
  }
};