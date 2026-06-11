# Baseline brainstorm — password reset via emailed link

## Requirements / behaviors

- **Request form**: User enters their email (or username) on a "Forgot password?" page and submits.
- **Account lookup**: System looks up the account by the submitted email.
- **Token generation**: On a valid request, generate a cryptographically random, single-use reset token (high entropy, not guessable/sequential).
- **Token storage**: Store a *hash* of the token server-side (not the raw token), associated with the user, with an issued-at and expiry timestamp.
- **Email delivery**: Send an email containing a reset link with the token embedded (e.g. `https://app.example.com/reset?token=...`).
- **Token expiry**: Reset links expire after a short window (e.g. 15–60 minutes); expired links are rejected.
- **Single use**: Once a token is successfully used to reset the password, it is invalidated immediately.
- **Reset form**: Clicking the link opens a page to enter a new password (with confirm-password field).
- **Token validation on landing**: Validate the token *before* showing the reset form so an invalid/expired token shows an error instead of a dead form.
- **Password update**: On submit with a valid token + valid new password, hash the new password (bcrypt/argon2/scrypt) and store it.
- **Password policy enforcement**: New password must meet strength rules (min length, complexity / breached-password check, etc.).
- **Token invalidation after use**: Invalidate the used token and any other outstanding reset tokens for that account.
- **Enumeration-safe response**: The request page returns the *same* generic confirmation ("If an account exists for this email, you'll receive a link") whether or not the email matches an account — to avoid leaking which emails are registered.
- **Confirmation email**: After a successful password change, send a notification email ("Your password was changed") to the account owner.
- **Session handling**: Optionally invalidate existing sessions / log out other devices after a successful reset.
- **Rate limiting**: Throttle reset *requests* per email and per IP to prevent abuse / email bombing.
- **Audit logging**: Log reset requests and completions (timestamp, IP, user agent) for security review.
- **HTTPS-only links**: Reset links must be HTTPS and point to the canonical domain.
- **Auto sign-in (decision)**: Decide whether a successful reset signs the user in directly or sends them to the login page.

## Edge cases & failure modes

- **Email not registered**: Show the generic confirmation; send no email (silently) — must not reveal non-existence.
- **Expired token**: Show "link expired" with an option to request a new one.
- **Already-used token**: Reject with a clear message; don't allow reuse.
- **Token reused after a *new* one issued**: Requesting a second reset should invalidate the first link (only the latest is valid) — decide and enforce this.
- **Multiple rapid requests**: User clicks "send link" several times → multiple emails; decide whether each invalidates prior tokens and how to message it.
- **Token tampering / forged token**: Random/invalid token values must fail validation cleanly (constant-time comparison to avoid timing attacks).
- **New password identical to old**: Decide whether to reject reusing the current/previous passwords.
- **New password fails policy**: Show validation errors without consuming the token (let them retry on the same page).
- **Password / confirm mismatch**: Client + server validation; don't consume token.
- **Email delivery failure / bounce**: Reset email never arrives (spam folder, hard bounce, provider outage); user has no feedback path beyond "check spam / try again."
- **Email link wrapping / prefetch**: Some mail clients/scanners prefetch links (auto-clicking the token) — a strict single-use GET could burn the token before the user clicks. Consider requiring a POST/confirmation step so a prefetch doesn't consume the token.
- **Token in URL leakage**: Tokens in the query string can leak via referrer headers, browser history, server logs, proxies — mitigate (short expiry, single use, scrub from logs, consider POST).
- **Account in special state**: Disabled / suspended / unverified-email / SSO-only / deleted accounts — decide whether reset is allowed and what message to show.
- **SSO / OAuth-only accounts**: Account may have no local password; reset flow should explain "you sign in with Google" rather than set a password.
- **Concurrent resets**: Two valid links somehow exist (race) → ensure only one can complete; second fails gracefully.
- **Clock skew / expiry boundary**: Tokens near the expiry boundary; use server time consistently.
- **Email change mid-flow**: User changes their email after requesting reset; the old link should still target the original account (or be invalidated by policy).
- **Long-lived link in old emails**: Old reset emails in inbox should be useless after expiry/use.
- **Rate-limit abuse / email bombing**: Attacker triggers many reset emails to a victim's inbox — throttle and possibly add CAPTCHA after N attempts.
- **Brute-forcing tokens**: Attacker guesses tokens — high entropy + rate limiting on the reset endpoint + lockout.
- **Case / whitespace in email**: Normalize email input (trim, lowercase) for lookup.
- **Internationalized email / Unicode**: Handle non-ASCII emails correctly.
- **User no longer has email access**: Recovery dead-end — out of scope here but worth flagging (needs alternate recovery).
- **Reset during active session**: User is already logged in and resets — keep current session valid or force re-auth?
- **Replay after success**: Hitting the same link again after success → "already used / link no longer valid."

## Open questions

- What is the **token lifetime** (15 min? 1 hour? 24 hours)?
- Should requesting a new reset **invalidate all prior** outstanding tokens, or keep them all valid until expiry?
- Should a successful reset **log out all other sessions / devices**?
- After reset, do we **auto-sign-in** the user or redirect to login?
- What is the **password policy** (min length, complexity, breached-password check via HIBP, password-history reuse ban)?
- Do we require the user to **re-enter their email/identity** on the reset page, or is the token alone sufficient?
- Should we use a **GET link or a POST/confirm step** to avoid mail-client prefetch consuming the token?
- What is the **rate-limit policy** (per email, per IP, per time window) and do we add CAPTCHA after a threshold?
- How do we handle **SSO-only accounts** that have no local password?
- What's the **confirmation/notification email** content and should it include an "I didn't do this" / revert link?
- What **email provider / deliverability** setup (SPF/DKIM/DMARC) and what's the fallback if email fails?
- What are the **localization / i18n** requirements for the email and pages (languages, RTL)?
- Are there **compliance / audit** requirements (retention of reset logs, PII handling)?
- Should the reset link be **device/browser-bound** or usable from any device?
- What **accessibility** requirements apply to the request and reset forms?
