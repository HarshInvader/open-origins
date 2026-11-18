# Donate your tokens

The fastest way to help Open Origins is to point your own AI agent, on your own subscription, at one of our open tasks. The project works on how life began with a human lead and a team of AI agents. Every token you donate is a test we could not otherwise afford to run.

## How

1. **Pick a task** from [board/TASKS.md](board/TASKS.md). Start with "Ready now"; the others wait on earlier results.
2. **Say you are taking it.** Open an issue named `Taking #<id>`, so two people don't run the same test.
3. **Give your agent this prompt**, with the task number filled in:

   > You are contributing to Open Origins, https://github.com/HarshInvader/open-origins. Clone it. Read docs/AGENT_BRIEF.md and follow its rules of evidence exactly. Then do task #<id> from board/TASKS.md. Write your plan, pass mark and fail mark in docs/prereg/<name>.md and add its sha256 to docs/prereg/HASHES.txt before you look at any outcome. Check the method recovers a planted answer first. Work only in experiments/<your_folder>/, write RESULTS.md with the verdict first, and report the result whichever way it goes. Then open a pull request.

4. **Open a pull request** with your `experiments/<folder>/`, the sealed pre-registration and its hash line.

## What we check before merging

- The pre-registration was sealed before the result (its hash and the PR history show this).
- The planted-answer check passed.
- The data split, nulls and pass marks are the ones you sealed.

A negative result counts as much as a positive one. Every positive result gets a red-team task, so someone else tries to break it before it goes on the site.

## Keep it light

- Download only what the task needs. Use the subsets and range reads described in the task, and never commit raw data.
- Don't contact researchers or data holders in the project's name. If a task needs data on request, say so in your issue and the lead will ask.

## Other ways to help

- **Break a result.** Pick any `RESULTS.md`, name your attack, seal your pass mark, run it.
- **Point us to data** we are missing. Open an issue with the link and its terms.
- **Tell us where we are wrong** about your field, with a source.

By contributing you agree your code is MIT licensed and your writing and results CC BY 4.0 (see [LICENSING.md](LICENSING.md)).
