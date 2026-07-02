// driver_10_guard.js — fail-loud input contract for the loom-pipeline driver.
//
// F4 (2026-07-03 dogfood): a resumed run rendered every args template slot as
// the literal string "undefined". Ground rules said "make the smallest
// reasonable assumption and proceed" — every station obeyed, intelligently
// and disastrously, and the pipeline silently drifted onto the wrong
// product. guardArgs() closes that hole: any required input that is
// missing, null, empty, or the literal string "undefined" throws instead of
// letting the run improvise.
//
// Self-contained: no imports, no Date.now/Math.random/argless new Date.
// Concatenated after driver_00_header.js in the build; must also parse
// standalone (`node --check`).

function guardArgs(args) {
  var FAIL_LOUD_NOTICE =
    "fail-loud: refusing to improvise missing inputs — no filesystem " +
    "hunting, no substitute seeds; the run FAILS rather than guessing.";
  var REQUIRED_FIELDS = ["segment", "changeId", "projectPath", "budgets", "models"];

  // Harness integration (observed live 2026-07-04, run wf_e96f6d0d-140):
  // the Workflow tool can deliver args as a JSON STRING. Parsing a valid
  // JSON object out of it is deterministic recovery, not improvisation —
  // anything else still fails loud below.
  if (typeof args === "string") {
    try {
      args = JSON.parse(args);
    } catch (e) {
      throw new Error(
        "guardArgs: args arrived as a non-JSON string (" + args.slice(0, 80) +
        "...). " + FAIL_LOUD_NOTICE
      );
    }
  }

  if (args === null || args === undefined || typeof args !== "object") {
    throw new Error(
      "guardArgs: expected an args object, received " + String(args) + ". " +
      FAIL_LOUD_NOTICE
    );
  }

  for (var i = 0; i < REQUIRED_FIELDS.length; i++) {
    var field = REQUIRED_FIELDS[i];
    var value = args[field];
    var isMissing =
      value === undefined ||
      value === null ||
      value === "" ||
      value === "undefined";
    if (isMissing) {
      throw new Error(
        'guardArgs: required input "' + field + '" is missing or invalid ' +
        "(received " + JSON.stringify(value) + "). " + FAIL_LOUD_NOTICE
      );
    }
  }

  // resumeRunId is optional, but the F4 leak was a literal "undefined"
  // string regardless of whether the field was required — guard it too.
  if (
    Object.prototype.hasOwnProperty.call(args, "resumeRunId") &&
    args.resumeRunId === "undefined"
  ) {
    throw new Error(
      'guardArgs: optional input "resumeRunId" leaked the literal string ' +
      '"undefined" (received "undefined"). ' + FAIL_LOUD_NOTICE
    );
  }

  // skillsRoot is optional at this guard layer (only segment 2 needs it —
  // driver_40_seg2.js throws its own fail-loud error when it is missing
  // there); when present it gets the same F4 "undefined"-string leak guard
  // as resumeRunId, plus an absolute-path shape check like projectPath.
  if (Object.prototype.hasOwnProperty.call(args, "skillsRoot")) {
    if (args.skillsRoot === "undefined") {
      throw new Error(
        'guardArgs: optional input "skillsRoot" leaked the literal string ' +
        '"undefined" (received "undefined"). ' + FAIL_LOUD_NOTICE
      );
    }
    if (typeof args.skillsRoot !== "string" || args.skillsRoot.charAt(0) !== "/") {
      throw new Error(
        'guardArgs: "skillsRoot", when present, must be an absolute path ' +
        'starting with "/" (received ' + JSON.stringify(args.skillsRoot) + "). " +
        FAIL_LOUD_NOTICE
      );
    }
  }

  if (args.segment !== 1 && args.segment !== 2 && args.segment !== 3) {
    throw new Error(
      'guardArgs: "segment" must be one of 1, 2, 3 (received ' +
      JSON.stringify(args.segment) + "). " + FAIL_LOUD_NOTICE
    );
  }

  if (typeof args.projectPath !== "string" || args.projectPath.charAt(0) !== "/") {
    throw new Error(
      'guardArgs: "projectPath" must be an absolute path starting with "/" ' +
      "(received " + JSON.stringify(args.projectPath) + "). " + FAIL_LOUD_NOTICE
    );
  }

  // changeId becomes a path segment (docs/loom/<changeId>/...) — allow-list
  // rather than deny-list: only [A-Za-z0-9._-] is safe there. A deny-list
  // (reject "/" and "..") lets shell-metacharacter ids like "foo$(x)"
  // through; an allow-list closes that hole by construction.
  var CHANGE_ID_ALLOWED_PATTERN = /^[A-Za-z0-9._-]+$/;
  if (!CHANGE_ID_ALLOWED_PATTERN.test(args.changeId) || args.changeId.indexOf("..") !== -1) {
    throw new Error(
      'guardArgs: "changeId" must match ' + CHANGE_ID_ALLOWED_PATTERN +
      " (letters, digits, dot, underscore, hyphen only; no \"..\") " +
      "(received " + JSON.stringify(args.changeId) + "). " + FAIL_LOUD_NOTICE
    );
  }

  return args;
}
