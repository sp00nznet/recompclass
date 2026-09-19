# Module 62: Research Methods

This module is about how to produce a result somebody else can rely on — which in this field
mostly means resisting a specific temptation: the thing works, the screenshot is good, and
you stop.

The techniques are all ones you have met. What is new is treating them as a *method* with an
order, rather than as debugging tools you reach for when stuck.

---

## 1. Start With a Question That Can Be Answered No

"Can Palm OS be statically recompiled?" is not a research question. It has no failure
condition, so no amount of work settles it.

These are:

- *What fraction of indirect transfers in a corpus of 400 Cybiko applications resolve
  statically after the address space is assembled correctly?*
- *How common is self-modifying code across 1,000 ZX Spectrum programs?*
- *Does pointer-scan-derived hinting improve or degrade discovery, measured on N targets?*

Each has a number at the end, and each could come back the way you did not want.

That last one is worth dwelling on. Module 14's `civrev` finding — 301 pointer-scan hints
made the build **worse**, 21 runtime-harvested hints fixed it — is a real result that
contradicts the intuitive answer. It was found by someone trying to make a game work, not by
someone studying hinting. **The field is full of results like that waiting to be measured
properly.**

---

## 2. Build the Oracle First

Module 38 §1, restated as method rather than practice, because in a research context it is
the difference between a result and an anecdote.

`encarta`'s first commits were the oracle, not the lifter. `tamarecomp` validated against
BrickEmuPy's independently-written E0C6200 core — *"precisely because that core was written
by someone else, from the same Epson documentation, in another language."*

If your conclusion depends on your implementation being correct, and the only check on your
implementation is the same conclusion, you have a circular result. An independent oracle
breaks the circle.

**The strongest form:** an implementation by someone else, in another language, from the
same primary source. **Acceptable:** your own interpreter, sharing no decode table with the
lifter. **Weak:** your own implementation sharing the decode table — it tests lifting, not
decoding, and you must say so.

---

## 3. Corpus, Not Examples

The single most common methodological failure in this field.

A technique demonstrated on one binary tells you it is possible. A technique measured across
a corpus tells you whether it works. These get conflated constantly, and the corpus versions
exist:

`gb-recompiled`: 1,592 of 1,609 ROMs (98.94%). `3dsnes`: 340 of 375 games (91%),
*"verified by an unattended run of the whole corpus rather than by spot-checks."*
`newtonrecomp`: `newtcc check unna.zip` stack-verifies a whole archive — and found the
`07 00 07` escape occurring **10,818 times**, always with operand 7.

That last one is the argument in miniature. The escape *silently corrupts every function
containing a `try` block*. On one example, you would never see it. Across an archive, the
stack fails to balance and tells you exactly where.

**Report the failures, categorised.** "17 of 1,609 failed" invites the question your reader
actually has. Module 33 §4's categories — extraction, codegen, compile, link, crash,
diverge — are five independent numbers.

---

## 4. Vary One Thing

Obvious, routinely violated, because in a recompilation project everything changes at once.

If you are measuring whether trace-guided discovery beats static solving, both arms must use
the same toolkit version, the same corpus, the same success criterion, and the same host.
`tamarecomp`'s validation had to **freeze the timers on both sides** to make the CPU
comparison meaningful — *"the test is about the CPU."*

Determinism is a prerequisite, not a nicety (Module 39 §3). A non-deterministic measurement
cannot distinguish an effect from noise.

---

## 5. Expect Your Harness to Be the Bug

Budget for this, because it happens every time and it will look exactly like a real finding.

`tamarecomp`'s validation doc records two before the real bug:

- Windows `stdout` is a **text stream** and expanded every `0x0A` in a binary trace into
  `0x0D 0x0A`. The giveaway was `X = 0x0A0D` — *an impossible value for a 12-bit register*.
- The reference advanced its oscillator inside every `clock()` while the runtime only moved
  time in `tama_step`, so one register read disagreed by a tick.

Both were harness bugs wearing CPU-bug costumes.

**The defence:** before believing a divergence, ask whether the *observed value is possible*.
A 12-bit register cannot hold `0x0A0D`. That single check caught a day-long red herring
immediately.

And: **prove your harness can detect a known bug.** Inject one you understand and confirm the
measurement finds it (Module 35 §1's "a check that cannot fail is not a check").

---

## 6. Negative and Partial Results Are Results

The field badly under-supplies both.

**Negative:** `encarta`'s `differential-test the 16-bit half too; instruction semantics are
clean` found nothing — and eliminated an entire layer from the search, which is what let the
next three commits find the real fault. Module 38 §6's rule: **use differential testing to
eliminate layers, not only to find bugs.**

Module 56's feasibility report ending in "do not do this, here is why" saves the next person
months and almost nobody publishes one.

**Partial:** `100% byte-exact over 168 of 216 columns` is more informative than either "it
works" or "it does not." It says the mechanism is right and the coverage is incomplete,
which is a different problem from either alternative.

---

## 7. Revise Downward When You Should

The methodological commitment that separates a result from a portfolio piece.

`tokyojungle`'s README: earlier builds advertised *35,208 lifted functions*; *"That number
was wrong, and the current one is lower on purpose"* — `find_functions` had been counting
intra-function basic blocks.

`xboxdashboard` retracted a screenshot and deleted 2,204 return-zero stubs.
`encarta` committed `retract "it decodes" - the buffers were copies of its own code`.

**If your numbers only ever go up, check how you are counting.** A measurement that cannot
decrease is not a measurement.

---

## 8. Make It Reproducible

The deliverable is not the number. It is the ability to get the number again.

- **One command** re-runs everything (`encarta`: *"One command that re-checks everything that
  works"*).
- **The corpus is identified** — not "1,609 ROMs" but which, by hash, or by a documented
  acquisition procedure if you cannot ship them (Module 45).
- **Versions are recorded** — tool, toolkit, compiler, host (Module 33 §6).
- **The measurement code is published**, even when the inputs cannot be.

Module 37's standard: **a number you cannot re-derive tonight is an impression.**

---

## 9. The Loop

1. Ask something that can be answered no.
2. Build the oracle.
3. Build the corpus.
4. Build the measurement, and prove it detects a bug you injected.
5. Measure. Vary one thing.
6. Suspect the harness first.
7. Report failures categorised, and partials honestly.
8. Publish the method with the number.
9. Revise downward when you should.

Steps 2 through 4 are most of the work, and they are what make step 5 mean anything. A
project that reaches step 5 in week one has usually skipped the part that makes the answer
true.

---

## Labs

- **Lab 120** -- Design a study: take one open problem from Module 61, write the question in
  falsifiable form, specify the corpus and success criterion, identify the oracle, and state
  what result would make you abandon the hypothesis.
- **Lab 121** -- Harness validation: build a measurement harness, inject three known bugs of
  different kinds, and confirm it detects each. Report any it missed and why.

---

**Next: [Module 63 -- Writing It Up](../module-63-writing-it-up/lecture.md)**
