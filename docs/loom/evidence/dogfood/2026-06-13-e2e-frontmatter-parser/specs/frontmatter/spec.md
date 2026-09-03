## ADDED Requirements

### Requirement: Parse a valid frontmatter block
The system MUST parse a leading `---` … `---` block of `key: value` lines into a
metadata dict and return the remaining text as the body.

#### Scenario: Single key-value pair
- GIVEN the text `---\ntitle: Hello\n---\nbody text`
- WHEN it is parsed
- THEN the metadata is `{"title": "Hello"}` AND the body is `body text`

#### Scenario: Multiple key-value pairs
- GIVEN the text `---\ntitle: Hello\nauthor: kouko\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{"title": "Hello", "author": "kouko"}` AND the body is `body`

### Requirement: Pass through text with no frontmatter
The system MUST return an empty metadata dict and the original text unchanged when the
text does not begin with a `---` delimiter line.

#### Scenario: Plain text with no frontmatter
- GIVEN the text `just a body, no frontmatter`
- WHEN it is parsed
- THEN the metadata is `{}` AND the body is `just a body, no frontmatter`

#### Scenario: Empty string input
- GIVEN the text `` (empty string)
- WHEN it is parsed
- THEN the metadata is `{}` AND the body is `` (empty string)

#### Scenario: Delimiter not on the first line is not frontmatter
- GIVEN the text `intro\n---\ntitle: x\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{}` AND the body is the original text unchanged

### Requirement: Reject malformed frontmatter loudly
The system MUST raise a ValueError when a frontmatter block is opened but malformed,
rather than silently treating it as body.

#### Scenario: Unclosed frontmatter block
- GIVEN the text `---\ntitle: Hello\nbody with no closing delimiter`
- WHEN it is parsed
- THEN a ValueError is raised

#### Scenario: Frontmatter line without a colon
- GIVEN the text `---\ntitle: Hello\nthisHasNoColon\n---\nbody`
- WHEN it is parsed
- THEN a ValueError is raised

#### Scenario: Empty key after stripping is malformed (critic-found)
- GIVEN the text `---\n: value\n---\nbody`
- WHEN it is parsed
- THEN a ValueError is raised
- AND likewise for a key that is only whitespace before the colon (`   : value`)

### Requirement: Handle frontmatter value and key edge cases
The system MUST handle empty blocks, colon-bearing values, surrounding whitespace,
duplicate keys, blank lines, and CRLF line endings deterministically.

#### Scenario: Empty frontmatter block
- GIVEN the text `---\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{}` AND the body is `body`

#### Scenario: Value containing a colon splits on the first colon only
- GIVEN the text `---\nurl: http://example.com\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{"url": "http://example.com"}`

#### Scenario: Surrounding whitespace on keys and values is stripped
- GIVEN the text `---\n  title  :   Hello World   \n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{"title": "Hello World"}`

#### Scenario: Duplicate keys keep the last value
- GIVEN the text `---\ntag: a\ntag: b\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{"tag": "b"}`

#### Scenario: Blank lines inside the block are skipped
- GIVEN the text `---\ntitle: Hello\n\nauthor: kouko\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{"title": "Hello", "author": "kouko"}`

#### Scenario: CRLF line endings are handled like LF
- GIVEN the text `---\r\ntitle: Hello\r\n---\r\nbody`
- WHEN it is parsed
- THEN the metadata is `{"title": "Hello"}` AND the body is `body`

#### Scenario: Empty value yields an empty string
- GIVEN the text `---\ntitle:\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{"title": ""}`

### Requirement: Pin the function contract (type, value-typing, fence exactness)
The system MUST treat non-string input as a type error, keep all values as strings
(no YAML coercion), and require fence lines to be exactly `---`. (All scenarios in
this requirement are `critic-found` — added by the completeness-critic panel.)

#### Scenario: Non-string input raises TypeError (critic-found)
- GIVEN a non-string input such as `None`
- WHEN it is parsed
- THEN a TypeError is raised (the parser does not coerce)

#### Scenario: Values are never coerced to non-string types (critic-found)
- GIVEN the text `---\nport: 8080\nflag: true\ntags: [a, b]\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{"port": "8080", "flag": "true", "tags": "[a, b]"}` (every value is a string)

#### Scenario: An opening line that is not exactly a fence is not frontmatter (critic-found)
- GIVEN the text `---extra\ntitle: x\n---\nbody`
- WHEN it is parsed
- THEN the metadata is `{}` AND the body is the original text unchanged (the first line is not a `---` fence)

#### Scenario: Body is empty when text ends at the closing fence (critic-found)
- GIVEN the text `---\ntitle: x\n---\n`
- WHEN it is parsed
- THEN the metadata is `{"title": "x"}` AND the body is `` (empty string)
