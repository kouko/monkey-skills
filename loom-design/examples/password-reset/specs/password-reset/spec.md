# Password reset via emailed link — spec delta

## ADDED Requirements

### Requirement: Request a password reset
The system MUST let an unauthenticated user request a password reset by
submitting an account identifier, and MUST respond identically whether or not an
account exists for that identifier.

#### Scenario: Reset requested for an existing account
- GIVEN an enabled account exists for the submitted email
- WHEN the user submits the forgot-password form with that email
- THEN the system mints a single-use, time-limited reset token bound to the account and sends an email containing the reset link

#### Scenario: Reset requested for a non-existent account (no enumeration)
- GIVEN no account exists for the submitted email
- WHEN the user submits the forgot-password form with that email
- THEN the system sends no email and returns the same response (and comparable timing) as the existing-account case, revealing nothing about account existence

#### Scenario: Repeated requests are rate-limited
- GIVEN a configured request threshold per identifier/IP window
- WHEN requests exceed the threshold within the window
- THEN the system throttles further requests without disclosing account existence

### Requirement: Mint a secure single-use reset token
The system MUST issue reset tokens that are high-entropy, stored hashed,
single-use, time-limited, and bound to exactly one account.

#### Scenario: A new request invalidates prior outstanding tokens
- GIVEN a reset token is already issued for an account
- WHEN the user submits a second reset request for the same account
- THEN the system invalidates the prior token so that only the most recent token is usable

#### Scenario: Token at the expiry boundary is rejected
- GIVEN a reset token whose expires-at time has been reached
- WHEN the user opens the link
- THEN the system treats the token as expired and refuses to show the set-password form

### Requirement: Validate the token before allowing a reset
The system MUST validate that a token exists, is unexpired, is not already
consumed, and is not invalidated before showing the set-password form, and MUST
NOT consume the token on a mere link-open (GET).

#### Scenario: Valid token opens the set-password form
- GIVEN an issued, unexpired, unconsumed token
- WHEN the user opens the link (GET)
- THEN the system shows the set-password form without consuming the token

#### Scenario: Email-scanner prefetch does not consume the token
- GIVEN a security scanner auto-fetches the link before the user clicks it
- WHEN the link is opened by a GET request
- THEN the token remains usable, because the token is consumed only on the password-submit action (POST)

#### Scenario: Already-consumed token is rejected (replay defence)
- GIVEN a token that has already been consumed by a successful reset
- WHEN the link is opened again
- THEN the system rejects it and does not show the set-password form

### Requirement: Enforce password policy on the new password
The system MUST validate the submitted new password against the configured
policy and MUST reject passwords that fail policy, match the confirmation field
incorrectly, or equal the current password.

#### Scenario: Password failing length/complexity policy is rejected
- GIVEN a configured minimum length and complexity policy
- WHEN the user submits a new password that violates the policy
- THEN the system rejects it with a policy message and does not change the password

#### Scenario: Confirmation mismatch is rejected
- GIVEN the set-password form requires a confirmation field
- WHEN the new password and its confirmation differ
- THEN the system rejects the submission and does not change the password

#### Scenario: New password equal to the current password is rejected
- GIVEN the new password equals the account's current password
- WHEN the user submits it
- THEN the system rejects it and does not change the password

### Requirement: Apply the reset atomically and consume the token
The system MUST update the password and consume the token as a single outcome,
SHALL surface a failure rather than leaving an inconsistent state, and MUST NOT
leave a usable token after a successful reset.

#### Scenario: Successful reset updates password and consumes token
- GIVEN a valid token and a policy-compliant new password
- WHEN the user submits the new password
- THEN the system updates the password, marks the token consumed, and the user can log in with the new password

#### Scenario: Token mint succeeds but email send fails
- GIVEN the reset token was minted
- WHEN the email send fails
- THEN the system surfaces the failure and allows the user to retry rather than silently leaving an orphaned token

### Requirement: Invalidate sessions on successful reset
The system MUST invalidate existing authentication sessions on a successful
password reset, and SHOULD invalidate persistent credentials such as
remember-me cookies and refresh/API tokens.

#### Scenario: Other active sessions are logged out after reset
- GIVEN the account has other active sessions at reset time
- WHEN the password reset succeeds
- THEN those sessions are invalidated and must re-authenticate with the new password

### Requirement: Notify the user of a password change
The system SHOULD send a notification to the account's verified address when the
password is changed, so the legitimate owner can detect an unauthorized reset.

#### Scenario: Change notification is sent on success
- GIVEN a password reset has succeeded
- WHEN the password is updated
- THEN the system sends a password-changed notification to the account's address

### Requirement: Deliver the reset link only over a secure channel
The system MUST embed the reset token only in HTTPS links and MUST NOT transmit
the token over an unencrypted channel.

#### Scenario: Reset link uses HTTPS
- GIVEN a reset email is generated
- WHEN the link is constructed
- THEN the link uses an HTTPS URL and the token is not exposed over plain HTTP
