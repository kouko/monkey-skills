# GNOME i18n Glossary

## Origin

The GNOME Translation Project glossary — historical EN↔target-language UI
terminology used across the GNOME desktop ecosystem.

Upstream repository: https://gitlab.gnome.org/GNOME/gnome-i18n
Glossary path:       `glossary/<locale>.po` (on the `master` branch)

## Files shipped

| File         | Source URL                                                                                |
|--------------|-------------------------------------------------------------------------------------------|
| `ja.po`      | https://gitlab.gnome.org/GNOME/gnome-i18n/-/raw/master/glossary/ja.po                     |
| `zh-CN.po`   | https://gitlab.gnome.org/GNOME/gnome-i18n/-/raw/master/glossary/zh_CN.po                  |
| `zh-TW.po`   | https://gitlab.gnome.org/GNOME/gnome-i18n/-/raw/master/glossary/zh_TW.po                  |

Note: the upstream filenames use underscore (`zh_CN.po`); this directory uses
hyphenated BCP-47-style filenames (`zh-CN.po`) to match the build script's
locale dispatch convention.

The `main` branch on GNOME's GitLab does not host the glossary at the
historical path; the `master` branch is current at the time of bundling
(2026-05-06).

## Refresh

```sh
cd translation-toolkit/vendor/gnome-i18n
curl -fsSL "https://gitlab.gnome.org/GNOME/gnome-i18n/-/raw/master/glossary/ja.po"    -o ja.po
curl -fsSL "https://gitlab.gnome.org/GNOME/gnome-i18n/-/raw/master/glossary/zh_CN.po" -o zh-CN.po
curl -fsSL "https://gitlab.gnome.org/GNOME/gnome-i18n/-/raw/master/glossary/zh_TW.po" -o zh-TW.po
```

## License

LGPL-2.1-or-later — see `LICENSE` in this directory.

GNOME glossary files are part of the GNOME Translation Project and inherit
the GNOME licensing posture. The bundled `LICENSE` is the canonical GNU
Lesser General Public License v2.1 text retrieved from
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt.
