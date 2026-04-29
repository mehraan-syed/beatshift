# AI Usage Reflection

## Tools Used

I used ChatGPT during development when I got stuck on something specific or wanted a second opinion on my work.

---

## Where I Used AI

### Requirements

I download FLAC files and they're always a mess. I knew what
I wanted the tool to do before I started writing anything down.

I did ask AI to look over my requirements once I had a draft:

> "Can you check these requirements for anything I might have missed?"

It pointed out I should add something about respecting MusicBrainz's rate
limits. I checked their website and they do have a 1-request-per-second
policy, so I added that as NFR-08.

### System Modelling

I hadn't used Mermaid diagrams before though, so I asked for help with
the syntax:

> "How do I write a class diagram in Mermaid?"

### Documentation

When writing the README I asked:

> "What sections should a good README have for a Python CLI tool?"

It gave me a list and I picked the ones that made sense for this project.
I skipped a few it suggested like "Contributing Guidelines" and "Code of
Conduct" since this is a coursework project not an open source one.

### Code

Most of the code I wrote myself, working through it module by module. There
were a few spots where I looked stuff up with AI:

- I asked how mutagen handles FLAC vs MP3 tags differently, because the
  documentation was a bit confusing. I found that FLAC uses simple key-value
  pairs but MP3 uses these frame objects with codes like TIT2 and TPE1.
- I asked what characters aren't allowed in Windows filenames when writing
  the sanitize function. I knew about the obvious ones but missed a few
  edge cases like dots at the start of filenames.

### Tests

I planned what to test myself mostly thinking about "what would break
this function?" For the boring repetitive stuff like setting up test
fixtures I got AI to help speed things up.

---

## Times I Had to Fix AI Output

### The pyproject.toml Disaster

Early on the AI gave me this for the build backend:

```toml
build-backend = "setuptools.backends._legacy:_Backend"
```

Completely broke the install. Got a big traceback about `BackendUnavailable`.
Looked it up and the actual correct value is `setuptools.build_meta`.

### Broken Test Logic

The duplicate detection tests failed because of a string matching
issue. The mock function checked `if "a" in f` to tell files apart, but
`/b.flac` has an "a" in "flac". So both files hit the same branch and
got flagged as duplicates when they shouldn't have been.

The actual duplicate detection code was fine — it was purely a test
writing mistake. Fixed it by using proper names like `/music/one.flac`
instead of single letters.

### Cross-Platform Path Issues

When I moved from my Linux machine to Windows for testing, one test
broke because of path separators (`/` vs `\`). Had to use
`os.path.normpath()` in the test so it passes on both.

---

## What AI Isn't Good At

**It can't run your code.** It'll write something that looks fine but
might not actually work. The pyproject.toml looked completely fine until I tried to install it.

**It adds stuff you don't need.** Every time I described what I was
building, it'd suggest extra features and more complex architecture.
Audio fingerprinting, plugin systems, config files none of which I
needed for this project.

**It makes subtle mistakes in tests.** The mock function bug was small
but took me a while to figure out.

---

## What I Learned

The most useful thing about using AI was that it forced me to
actually check everything. Because I knew the output might be wrong I had to read it, understand it, and
test it. That probably made me engage with the code more than I would
have if I'd just been copying from Stack Overflow.

If I did this again I'd probably use AI less for generating lines of code when i was tired
and more for targeted questions.I'd write it myself and then ask "is there a better way to
handle this edge case?" That way I'd understand the code better and could maybe find more efficient ways of
handling functions.
