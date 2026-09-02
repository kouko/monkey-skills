# Interview question bank

Every question here is tagged with its type. `what` is the only type this
station may ask: what do you want, what happens today, what would you be
able to do. `behaviour` ("you type X and you see Y") belongs to
`write-spec`, and `done` ("did it work") to acceptance at the end — they
are listed nowhere in this file, on purpose.

Ask one question at a time and let the answer choose the next one. Reject
an aspiration offered as an answer: when the reply stays abstract, ask for
an example rather than accepting confidence as evidence.

## Engineering — ask four to six

1. **(what)** What goes wrong today, and who notices it?
2. **(what)** What do you or the team do instead right now, each time it
   happens?
3. **(what)** When this is finished, what will you be able to do that you
   cannot do today? Give me one sentence per thing.
4. **(what)** What must not change while we do it — anything that would
   break for someone else?
5. **(what)** Is anything already fixed: language, platform, a service we
   pay for, a data format we cannot move?
6. **(what)** What is explicitly out of scope this time?

Three to five lines of intent is a complete engineering intent. Stop when
Problem, Proposed outcome, Acceptance, Constraints and Out of scope can be
filled in without guessing.

## Product — ask eight to ten

1. **(what)** Who is this for? Describe one of them.
2. **(what)** What are they trying to get done, and how do they do it
   today — including the workarounds?
3. **(what)** What is the worst part of doing it that way?
4. **(what)** When this is finished, what will they be able to do? One
   sentence each, in their words.
5. **(what)** How would you know it worked, without asking me?
6. **(what)** What must it never do?
7. **(what)** Is anything already decided that cannot change — platform,
   language, a paid service, a data format?
8. **(what)** What happens if we get it wrong — who is hurt, and how badly?
9. **(what)** What is out of scope for this change?
10. **(what)** Is there anything you already know users will ask for next,
    that we are deliberately not doing now?

## Value case — ask all three, product only

1. **(what)** Why now rather than later or never? What changes if you wait?
2. **(what)** Why build it rather than use something that already exists,
   or do nothing?
3. **(what)** What concretely loses this time — what will you not do
   instead? If nothing is displaced, the appetite is hollow.

End with GO or NO-GO and one reason. One weak answer alongside two
concrete ones can still be a GO — name the weak one. Two or more weak
answers are a NO-GO for now, never a hopeful GO. A NO-GO is written into
the intent as `status: withdrawn — <reason>`; the reasoning is preserved so
nobody re-argues it blind.

## One bad / good pair per section

**Engineering.**
Bad: "Should the six scripts share a helper module or a base class?" — the
user would have to read the scripts to answer; it is a design fork you
decide yourself and note the reason.
Good: "What goes wrong today when one of those scripts changes?" — they
can answer from their own experience, and the answer becomes Problem.

**Product.**
Bad: "Do you want the due date stored as an ISO string or a timestamp?" —
storage is invisible to the user; nothing in their answer would be
evidence.
Good: "When this is finished, what will you be able to do with a due
date?" — the answer is an Acceptance line, provable by someone running the
change for the first time.

**Value case.**
Bad: "Is this valuable?" — no answer to that is falsifiable.
Good: "What will you not do this month if you do this instead?" — names a
real competing commitment, or reveals there is none.

## Writing the answers down

Acceptance lines are the load-bearing output: each one must be provable by
someone who has never seen the change, running it in a clean environment.
Rewrite anything that is not. "The code is cleaner" fails. "I can set a due
date when I add a task, and see it in the list" passes.

Keep a running list of every question you actually asked, with its type, to
pass forward at hand-off.
