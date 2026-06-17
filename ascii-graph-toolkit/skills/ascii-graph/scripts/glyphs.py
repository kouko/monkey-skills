"""Canonical box-drawing glyph taxonomy — SSOT for the check modules (de-facto 1-cell: box-drawing/block glyphs are special-cased narrow in ~all terminals)."""

VERTICALS = frozenset("│┃║┆┇╎╏")           # light, heavy, double, dashed verticals
HORIZONTALS = frozenset("─━═┄┅┈┉╌╍")        # light, heavy, double, dashed horizontals
CORNERS = frozenset("┌┐└┘╭╮╰╯┏┓┗┛╔╗╚╝")    # light, rounded, heavy, double corners
TEES = frozenset("├┤┬┴┼┣┫┳┻╋╠╣╦╩╬")        # light, heavy, double tees/crosses
ARROWS = frozenset("▼▲►◄◀▶→←↑↓")

JUNCTIONS = CORNERS | TEES                  # glyphs that legitimately end/branch a vertical seam
VERTICAL_CONNECTORS = VERTICALS | frozenset("▼▲↑↓")  # participate in a vertical seam run
BOX_BORDER = HORIZONTALS | CORNERS | TEES    # horizontal extent an arrowhead must land within
STRUCTURAL = VERTICALS | JUNCTIONS | HORIZONTALS | ARROWS
