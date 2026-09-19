#!/usr/bin/env python3
"""
Build the project and writing labs -- the ones with nothing to unit-test.

These are README-only by design. A lab that asks you to audit three real
repositories, profile a real binary, or get a contribution merged cannot be
checked by pytest, and pretending otherwise would be exactly the kind of
check-that-cannot-fail Module 35 warns about.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from make_lab import lab, report

E = "\n**Deliverable:** a written report in your project repository.\n"

lab(56, "Break Your Own CI", readme="""
    ## Objective

    Prove that every gate in your CI can actually fail.

    ## Background

    Module 35 opens with a real bug from this repository: a job called "Run
    Python labs" that ran `python test_lab.py`, which defines pytest classes
    and exits 0. It passed on every commit for months and tested nothing, while
    a genuine `NameError` sat in a shared lab helper.

    **A CI step that cannot fail is worse than no CI step**, because it converts
    "untested" into "tested" in every reader's head, including yours.

    ## Your Task

    Take a pipeline with CI (yours, or the one from Lab 59) and, for each gate:

    1. Introduce a real defect of the kind that gate exists to catch.
    2. Run CI. Confirm it goes red, and that the message names the problem.
    3. Revert.

    Defects worth trying: a syntax error in a generated file; a lifter change
    that alters golden output; a deleted runtime symbol; a test that imports a
    module that no longer exists; a solution left stale after a stub change.

    ## Report

    A table of gate, defect injected, did it fail, and how legible the message
    was. **Any gate that stayed green is the finding** -- write up why, and
    either fix it or delete it.
    """ + E)

lab(59, "Unit 9 Capstone: A Pipeline That Survives Being Broken", readme="""
    ## Objective

    Combine Labs 51-58 into one pipeline that takes a target from container to
    built binary, caches correctly, is driven by a manifest, and gates on
    something real.

    ## Your Task

    **Build the pipeline.** Stages from extraction through to a compiled
    artifact, with content-hash caching (Lab 51) and a provenance record.

    **Drive it from a manifest** (Lab 57). Every decision in the file, nothing
    in your shell history. Hints commented with where they came from.

    **Make it batch** (Lab 52). Several targets, isolated, with categorised
    failures and a machine-readable report.

    **Add the checks.** Fallthrough detection (Lab 54) and a synthetic fixture
    suite (Lab 55) in CI.

    **Then break it on purpose** (Lab 56), at every stage, and confirm every
    gate goes red.

    ## Deliverable

    A repository where three commands take a clean checkout to a built artifact,
    plus a report covering: what the cache saves on a warm run, the batch report
    for your corpus with failures categorised, and the break-it table from Lab 56.

    ## What Good Looks Like

    Someone else clones it, follows the README, and gets the same numbers you
    did. Module 37's standard: a result you cannot re-derive is an impression.
    """)

lab(60, "Audit Three Projects", readme="""
    ## Objective

    Apply Module 37's ten-minute audit to three real recompilation repositories,
    one of which is your own.

    ## Background

    The audit, from Module 37 section 6:

    1. **Read the `.gitignore` first.** It tells you whether the interesting half
       of the project is even present, and therefore what any other observation
       can prove.
    2. **`ls src/` for hand-written names.** `fe_menu.c`, `rw_renderer.c`,
       `static_textures.c` are harness. Generated output is thousands of
       `sub_XXXXXXXX` functions in numbered files.
    3. **`wc -l` both groups.**
    4. **Audit the toolkit, not the port.** If the toolkit is emulator-hosted,
       no port on it can claim more than the toolkit allows.
    5. **Find the fallback. Is it silent?**
    6. **What drives the frame loop** -- the game, or the project's code?
    7. **Look for the counters.**

    ## Your Task

    For each of three projects, produce a one-paragraph evidence assessment and
    place it on the **ladder of evidence** (Module 37 section 5).

    Be specific. "The README claims X; `src/foo.c` line N does Y" is an
    assessment. "Seems overstated" is not.

    ## Report

    Three assessments, each naming its rung and the evidence for it. For your
    own project, say what you will change as a result.

    Be fair: the goal is accuracy in both directions. A project that is *more*
    impressive than its README claims is also a finding worth reporting.
    """ + E)

lab(71, "Unit 10 Capstone: Differential Fuzzer with Nested Minimisation", readme="""
    ## Objective

    Combine Labs 62-70 into a loop that finds a divergence, shrinks it, locates
    the responsible function, and produces a claim that survives an audit.

    ## Your Task

    **Oracle** (Lab 62). Independent if you can get one -- Module 53's project
    used a core written by someone else, in another language, from the same
    datasheet.

    **Fuzz** (Lab 65, 66). Randomised inputs through both implementations,
    deterministic and replayable, detecting the first divergence.

    **Minimise twice.** Input bisection (Lab 66), then code bisection (Lab 63)
    to find the function.

    **Tripwire** (Lab 64). Boundary assertions so silent corruption surfaces at
    the call that caused it.

    **Keep every reproducer** as a regression test.

    ## Deliverable

    A one-command differential run, a corpus of minimised reproducers, and for
    each finding: the minimal input, the implicated function, and the divergence.

    ## The Part That Is Graded

    An **evidence statement** for your result that would survive Module 37's
    audit. State your rung, how you measured, what you did not test, and one
    thing you ruled out. If your fuzzer found nothing, say that -- and say what
    would have to be true for that to be good news rather than a broken harness.
    """)

lab(72, "Profile a Recompiled Binary", readme="""
    ## Objective

    Profile a real recompiled binary on a real workload and find out where the
    time actually goes.

    ## Background

    Module 41's warning: your intuitions were formed on hand-written code, and
    this is not hand-written code. The time is usually **not** in the lifted
    code -- it is in the runtime, memory access, dispatch, or graphics.

    And the number that governs everything: `wormsrevolution` lifted 88,816
    functions and reaches 444.

    ## Your Task

    1. Build with symbols and frame pointers.
    2. Profile a **real workload** -- gameplay, not boot-to-title.
    3. Produce a ranked breakdown separating: runtime, generated code, dispatch,
       graphics translation, memory access.
    4. Report **what fraction of lifted functions executed at all.**
    5. Pick one baseline from Module 41 section 2 and say how you compare.

    ## Report

    The breakdown, the executed-function fraction, and one sentence on whether
    the result surprised you. Include the command that re-runs the measurement.

    If you are slower than a mature emulator of the same system, stop and find
    the structural mistake -- that is a finding, not a failure.
    """ + E)

lab(80, "Unit 11 Capstone: Measured Optimisation", readme="""
    ## Objective

    Profile a recompiled title, optimise its ten hottest functions, and prove
    behaviour did not change.

    ## Your Task

    **Profile first** (Lab 72). Whole binary, real workload.

    **Apply targeted optimisations** from Unit 11: memory access (Lab 76),
    endianness (Lab 77), SIMD where the guest used vectors (Lab 74), pruning
    (Lab 78), function ordering (Lab 79).

    **Measure after each one**, separately. A combined "we made it 3x faster" is
    not a result you can act on later.

    **Prove correctness held.** Every technique in Unit 11 changes what code
    exists or where it lives. Run your Unit 10 differential test after each step.

    ## Report

    Before and after per optimisation, with a re-runnable measurement command.
    Report the **99th percentile frame time**, not the mean -- for a game the
    question is whether any frame missed its deadline.

    ## What Good Looks Like

    An optimisation you tried that did **not** help, written up with why. Module
    62 section 6: a negative result is a result, and this is the unit where
    people quietly discard them.
    """)

lab(81, "Dependency Audit", readme="""
    ## Objective

    Enumerate every third-party component in a recompilation project, its
    licence, and how it is linked -- then say whether the project's declared
    licence is compatible with all of it.

    ## Background

    Module 45 section 3. `snesrecomp` can be permissive because LakeSnes is
    **MIT**; had it been GPL, every port linking it would inherit that. This is
    an architectural constraint, not paperwork: retrofitting a licence change
    onto a project that links a GPL emulator means replacing the emulator.

    *This lab is not legal advice.* It is an inventory exercise.

    ## Your Task

    For a project of your choice (ideally your own):

    1. List every third-party component -- vendored source, submodules, linked
       libraries, tools your build shells out to.
    2. For each: its licence, its version, and **how it is linked** (static,
       dynamic, vendored, invoked as a subprocess).
    3. Note anything with no licence at all. "It's on GitHub" is not a licence.
    4. Produce a `NOTICE` file preserving every required notice.
    5. State whether the declared licence is compatible with everything above.

    ## Report

    The inventory table, the `NOTICE` file, and your compatibility conclusion
    with reasoning. Flag anything you could not determine rather than guessing.
    """ + E)

lab(82, "Ship-the-Tool Workflow", readme="""
    ## Objective

    Restructure a project so a user with their own copy can go from binary to
    running build with documented commands -- and so a fresh clone contains no
    copyrighted material.

    ## Background

    Module 45 section 1. Every port in the corpus says a version of *"bring your
    own disc; no game files included"*, and the architectural consequence is
    that **the recompiled output is gitignored too, not just the ROM**.

    ## Your Task

    1. Audit what a fresh clone contains. Anything derived from the original
       binary?
    2. Fix the `.gitignore` -- ROM, assets, **and generated output**.
    3. Document the user's path: where their copy goes, what commands to run,
       what they will see.
    4. Verify: clone into a clean directory and confirm nothing copyrighted is
       present.
    5. Note what this costs you in verifiability (Module 45 section 2) and say
       so in the README.

    ## Report

    The before/after of what ships, the user-facing commands, and a paragraph on
    which of your README's numbers a reader can and cannot check.
    """ + E)

lab(84, "Fresh-Machine Run", readme="""
    ## Objective

    On a machine that has never seen your project, follow only your own README.

    ## Background

    Module 46's least glamorous claim: most projects fail not because the
    recompilation was wrong, but because nobody else could ever run it.

    ## Your Task

    Use a clean VM, a container, or a friend. The rule is absolute: **follow
    only what is written.** No filling gaps from memory, no fixing things
    silently.

    Record every point where you had to know something undocumented -- a tool
    version, an environment variable, a directory that must exist, an error
    whose meaning is not obvious.

    Then fix the documentation and do it again until the run is clean.

    ## Report

    The list of gaps found on the first pass, what you changed, and how many
    passes it took. If you used another person, record the questions they asked
    -- each one is a documentation bug.

    ## What Good Looks Like

    A second person completes it without asking you anything.
    """ + E)

lab(85, "Runtime Feature Set", readme="""
    ## Objective

    Add the features users expect: save states, rebindable input, and saves in
    the platform-correct location, behind an overlay.

    ## Background

    Module 47 section 1. The baseline across finished ports in the corpus:
    `LinksAwakening` has save states, rebindable gamepad and keyboard, an ImGui
    debug overlay and an asset viewer; `diddykongracing` has a settings window
    on F1, a debug overlay on F2, and EEPROM saves written to AppData.

    Save states are nearly free -- your entire guest state is a struct and an
    array -- and they change how people use your build, including you while
    debugging.

    ## Your Task

    1. **Save states.** Serialise and restore guest state. Handle the
       runtime-side state too (timers, pending interrupts).
    2. **Rebindable input**, persisted.
    3. **Saves in the right place** -- the platform convention, not next to the
       executable.
    4. **An overlay** exposing all of it.
    5. Build it in the **toolkit**, not the game (Module 47 section 1).

    ## Report

    What you built, where it lives (toolkit or port), and one debugging task
    that got easier because save states exist.
    """ + E)

lab(86, "Write a Mod", readme="""
    ## Objective

    Override one function in a recompiled game with your own C implementation,
    using an auto-registering patch macro.

    ## Background

    Module 47 section 3, and the mechanism is a direct consequence of Module
    14's dispatch table. From `snesrecomp`'s `recomp_patch.h`:

    > **Mod / override pattern:** link a second `.obj` that defines another
    > `RECOMP_PATCH` at the same SNES address with a different function name.
    > **The last constructor to run wins**, so put mod objects after the original.

    Overriding a shipped game function is a **link-order question**. A modder
    writes a C function -- with types, a debugger, and no space constraint --
    and it replaces the original at the address the game calls.

    ## Your Task

    1. Pick a function whose effect you can see.
    2. Write a replacement in C, satisfying every caller's expectations:
       calling convention, register effects, and any memory the original wrote.
    3. Link it after the original and confirm yours runs.
    4. **Record the game revision it targets** -- addresses move (Module 46
       section 2).
    5. Document the link order.

    ## Report

    The mod, the documented link order, the revision it targets, and what went
    wrong the first time. Something will: the usual culprit is state the
    original function wrote that yours does not.
    """ + E)

lab(96, "Feasibility Report", readme="""
    ## Objective

    Pick a target nobody has recompiled, run every measurement in Module 56
    section 1, and write a report that ends in a recommendation -- **including
    "do not".**

    ## Your Task

    In order, stopping early if an answer disqualifies it:

    1. **Is it machine code?** Imports and relocation density against a
       known-native binary of similar size (Module 54 section 1).
    2. **Can you get a copy legally, and say so plainly?**
    3. **Can you reach plaintext code?**
    4. **Is there an independent implementation you can run?** The single best
       predictor of whether this goes smoothly.
    5. **How much resolves statically?** Assemble the *whole* address space
       first (Module 55 section 2), then count unresolved transfers and
       **classify them by defining instruction**.
    6. **Is there a decomp, symbol file or SDK?**
    7. **How big is the OS import surface?**

    ## Report

    The measurements with their methods, the shape of the work, your target rung
    on Module 37's ladder, your proposed first game, the biggest unknown, and a
    recommendation.

    ## What Good Looks Like

    A well-documented "this is not worth doing, here is why" is a real
    contribution and almost nobody publishes one (Module 59 section 6). If that
    is your conclusion, it is a complete answer to this lab.
    """ + E)

lab(97, "Front-End Reuse Audit", readme="""
    ## Objective

    Take two toolkits that share a CPU, diff their front ends, and report what
    is genuinely machine-specific versus what drifted apart and should be shared.

    ## Background

    Module 34 section 3. `vic20recomp`'s README states that its decoder,
    flag-correct ALU, analyzer, C emitter and interpreter oracle are *the same
    battle-tested 6502 front end* that recompiled Apple II games -- only the
    machine around them changed.

    The design rule that enables it: **your lifter must not know what a memory
    address means.** It emits `bus_read8(addr)` and stops.

    ## Your Task

    Pick two toolkits sharing a CPU -- `apple2recomp` and `vic20recomp`, or any
    two of the Z80 family (`tirecomp`, `zxrecomp`, `pacrecomp`, `galaxrecomp`).

    1. Diff the decoder, ALU, analyzer and emitter.
    2. Classify every difference: genuinely machine-specific, an improvement
       only one side received, or accidental drift.
    3. Find any place a lifter special-cases an address because of what it
       means on that machine.

    ## Report

    The classification with examples, and a recommendation for what should be
    shared. Estimate what unifying them would cost and what it would buy.
    """ + E)

lab(98, "Unit 14 Capstone: A New Architecture", readme="""
    ## Objective

    Take a target nobody has recompiled from feasibility report to a
    differentially-validated decoder.

    ## Your Task

    **The report** (Lab 96). Do not skip it; it decides the rest.

    **The decoder.** Table-driven (Module 34 section 2), with a control-flow
    class per opcode. Generate the table from a machine-readable ISA description
    if one exists.

    **The interpreter oracle**, generated from the same table (Lab 62).

    **Differential validation** (Lab 89). Against an independent implementation
    if one exists -- Module 53's standard is *"written by someone else, from the
    same documentation, in another language."* Against real hardware if not.

    **A machine document** (Lab 115) separating published fact from inference.

    ## Deliverable

    A toolkit repository with no ROMs in it, a decoder, an oracle, a validation
    report, and machine documentation.

    You do **not** need a running program. Module 59's shapes: a toolkit is done
    when a second program works on it, and a research log is done when the
    question is answered. Say which you are delivering.

    ## What Good Looks Like

    Your validation found something, and you wrote it up -- including any harness
    bugs that impersonated target bugs (Module 62 section 5).
    """)

lab(101, "Patch Versus Recompile", readme="""
    ## Objective

    Implement the same behaviour change twice -- as a byte patch and as a
    recompiled override -- and compare.

    ## Background

    Module 50 section 4. The corpus patches constantly: `diddykongracing`
    neutralises three anti-piracy checks; `--protect_zero=false` changes
    behaviour without changing code.

    And the inversion worth testing: **once a program is recompiled, patching
    gets easier, not harder.** A ROM hack must not change any size; a recompiled
    program's patch is a C function with a debugger and no space constraint.

    ## Your Task

    Pick a behaviour you can see and change it both ways.

    **As a byte patch:** find the bytes, change them, keep the size identical.
    **As a recompiled override:** replace the function in C (Lab 86).

    Compare: effort, fragility across revisions, what each lets you do next,
    debuggability, and what happens when you get it wrong.

    ## Report

    Both implementations, the comparison, and a recommendation for when each is
    right. Note whether the recompiled version let you do something the patch
    could not -- extra state, a longer string, a call to a host library.
    """ + E)

lab(102, "Read the Adjacent Literature", readme="""
    ## Objective

    Read one paper from the binary rewriting community and report what transfers.

    ## Background

    Module 50 section 2. The security and systems communities have been working
    on your problems for thirty years under different names -- they say
    "rewriting" and "binary analysis" where preservation people say
    "recompilation". Searching the other field's terms finds solved problems.

    ## Your Task

    Pick one:

    - **RetroWrite** (Dinesh, Burow, Xu & Payer, IEEE S&P 2020) -- static
      rewriting for fuzzing and sanitization; recovers relocation information.
    - **rev.ng** (Di Federico, Payer & Agosta, CC 2017) -- lifts to LLVM IR,
      recovers CFGs and **function boundaries** (Module 34's root cause).
    - **BinRec** (Altinay et al., EuroSys 2020) -- dynamic traces guiding static
      lifting; the formal version of Module 49 section 4.
    - **LeanBin** (Wodiany, Pop & Luján, arXiv 2024) -- lifting for debloating;
      Module 44's 444-of-88,816 problem from a security motivation.

    ## Report

    One page: what problem it solves, what technique it uses, what transfers to
    a recompilation project in this course, and what does not -- with reasons.

    Be specific about the mismatch. These tools target server software, which
    has different properties from game binaries. Where their evaluation would
    not hold on your targets, say so.
    """ + E)

lab(105, "Feed Back", readme="""
    ## Objective

    Produce an artifact useful to a decompilation project and offer it upstream.

    ## Background

    Module 51 section 6. The relationship goes both ways, and this is the part
    most recompilation projects miss. Your recompiler produces things a decomp
    team wants and cannot easily generate:

    - **Function boundaries** your recursive descent found that their hand work
      has not reached.
    - **Execution traces** ranking their unmatched functions by how often they
      actually run -- a prioritisation they otherwise guess at.
    - **Divergence reports.** If your output and their matching C disagree,
      exactly one of you is wrong.

    ## Your Task

    Pick a target with an active decompilation project. Produce one of the above,
    in a format they can use -- ask first rather than inventing one.

    Then offer it. Approach as a peer: their work deleted an entire phase of
    yours (Module 51 section 2), so lead with what you can give back.

    ## Report

    The artifact, how you generated it, the response, and what you learned about
    their workflow. A polite decline is a valid outcome and still worth writing
    up -- note why it was not useful.
    """ + E)

lab(108, "Unit 13 Capstone: Move Along the Spectrum", readme="""
    ## Objective

    Take a project that is purely static or purely interception-based and move
    it one step along Module 49's spectrum.

    ## Your Task

    Pick one:

    **Add trace-guided discovery** to a static project. Record a playthrough,
    harvest entry points, and measure the change in discovered functions and
    unresolved transfers. Compare against pointer-scan hinting -- Module 14's
    `civrev` found 301 scan hints made things *worse* and 21 runtime-harvested
    hints fixed it.

    **Add an interpreter fallback** to a project that currently returns zero on
    a miss, and measure how often it fires.

    **Add a migration path** to an interception project: auto-registration
    (Lab 112), the A/B lever (Lab 63), and the crossover metric (Lab 99).

    ## Report

    The crossover metric before and after -- what fraction of executed
    instructions run as native code -- plus what the change cost in complexity.

    ## The Honest Part

    State your project's position on Module 49 section 6's table, and check
    whether your README describes the architecture you actually have. The
    corpus's clearest failure is not a bad design choice; it is a good design
    choice described as something else.
    """)

lab(109, "Upstream a Fix", readme="""
    ## Objective

    Find a genuine bug in a toolkit you use, minimise it, and get it merged.

    ## Background

    Module 57. `lttp-recompiled` contains no code and produced **ten upstream
    fixes** to the toolkit it was stressing. A serious port is the best
    bug-finder a toolkit can have, because your target uses a different subset
    of the machine than its author's did.

    ## Your Task

    1. **Find one.** Not a feature request -- a case where the toolkit does the
       wrong thing.
    2. **Minimise it** (Module 39 section 4): shrink the input, then bisect the
       code.
    3. **Isolate it from your project.** If it reproduces with a synthetic
       fixture, the maintainer needs nothing of yours.
    4. **Bring differential evidence**: ours emits X, the reference produces Y,
       here is the state at divergence.
    5. **Bring a test** that fails before and passes after.
    6. **Say what you ruled out.**
    7. Submit it.

    ## Report

    The bug, the minimal reproducer, the evidence, and what happened. A rejected
    patch with a stated reason is a complete answer -- write up the reason.

    If you cannot share the binary it was found on, say so up front and describe
    the shape instead.
    """ + E)

lab(110, "Fill a Named Gap", readme="""
    ## Objective

    Implement something a project has explicitly documented as missing.

    ## Background

    Module 57 section 4. `ps3recomp`'s `docs/MODULE_STATUS.md` tracks every HLE
    module as Not Started / Stubbed / Partial / Complete -- which doubles as a
    contribution roadmap. **Check it first; it moves.**

    The shape to look for: **the plumbing is done and the payload is missing.**
    `cellVdec` sequences callbacks correctly and never decodes a frame. That is
    an unusually good contribution target, because the interface is pinned down
    by a working caller, so you can tell immediately whether you are right.

    ## Your Task

    1. Find a gap a project has named as open.
    2. Confirm it is still open, and say so in your first message.
    3. Implement against the interface its existing callers already define.
    4. Verify -- ideally differentially, against whatever the real thing did.
    5. Submit with your verification method.

    ## Report

    The gap, your implementation, how you verified it, and the outcome. Include
    what the existing callers told you about the interface that the
    documentation did not.
    """ + E)

lab(111, "Extract a Toolkit", readme="""
    ## Objective

    Split a single-game project into a toolkit and a port, then bring up a
    second, deliberately different game on it.

    ## Background

    Module 58. The line goes at **"is this true of the machine, or of this
    program?"** And Module 58 section 2: a toolkit with one port is one project
    with delusions of generality -- you cannot tell which decisions are general
    until something else has to live with them.

    The target to aim at: `wormsrevolution`'s entire hand-written surface is four
    files, 8.5 KB, of which `main.cpp` is **146 bytes**.

    ## Your Task

    1. **Split.** Machine-general code to the toolkit; program-specific to the
       port.
    2. **Confirm the port still works**, unchanged in behaviour.
    3. **Bring up a second game** that differs in one specific way -- a different
       mapper, compiler, or peripheral. Same-again proves nothing.
    4. **Record every place the split forced a change.** These are the
       assumptions you did not know you had made.
    5. Add auto-registration (Lab 112) and a worked example to the tree.

    ## Report

    The before/after structure, the size of the per-game surface for both games,
    and the list of forced changes. That list is the actual deliverable.
    """ + E)

lab(113, "Classify the Corpus", readme="""
    ## Objective

    Assign a project shape to fifteen public recompilation repositories, and note
    where the README's framing and the repository's contents disagree.

    ## Background

    Module 59's nine shapes: toolkit, first game, second game, flagship port,
    stress target, research log, preservation case, novel capability, harness.
    Each has a different "done" condition and a different metric.

    Most misread projects are shapes described as other shapes.

    ## Your Task

    For each of fifteen repositories:

    1. **What shape is it**, from the contents?
    2. **What shape does the README imply?**
    3. **What is its "done" condition**, and has it been met?
    4. **What metric is it measured by**, and does the project report it?

    ## Report

    A table, plus a short note on every disagreement between framing and
    contents. Then: **which shape is most under-represented**, and what does
    that say about where the easy contributions are?

    Be fair. A project whose README undersells it is as much a finding as one
    that oversells, and Module 59 section 10's point is that seven of the nine
    shapes do not require a playable game at all.
    """ + E)

lab(114, "Declare a Shape", readme="""
    ## Objective

    Write the first paragraph of your own project's README, declaring its shape,
    its "done" condition, and the metric it should be judged by -- then check
    whether your recent work was aimed at that metric.

    ## Background

    Module 59 section 10: pick before you start, say which in the first
    paragraph, and match your measurement to your shape. Function counts for a
    toolkit, a rung on the ladder for a port, upstream fixes for a stress target,
    categorised failures for a harness.

    Module 37's complaint is not that projects measure the wrong things. It is
    that they measure **whatever goes up**.

    ## Your Task

    1. Write the paragraph. Shape, done condition, metric.
    2. Review your last month of commits. What were they aimed at?
    3. If the answer is "not that metric", say what you will change -- the plan
       or the work.
    4. If your shape has changed since you started, announce it.

    ## Report

    The paragraph, the commit review, and your conclusion. A finding of "my
    stated goal and my actual work have diverged" is the most useful outcome
    here and the most common.
    """ + E)

lab(115, "Machine Document", readme="""
    ## Objective

    Write the ISA and memory-model notes for a target you have worked on,
    marking every statement as published fact or inference.

    ## Background

    Module 60 section 3. Project documentation is current-state and goes stale.
    **Machine documentation outlives your project entirely** -- someone writing
    an emulator, a disassembler or a different recompiler wants it.

    `vmurecomp`'s `docs/CPU.md` sets the standard in its opening lines:

    > This is not a datasheet -- it records the decisions the decoder and runtime
    > had to make, and **which of them rest on published facts versus convention**.

    Six months on you will not remember which of your facts came from a datasheet
    and which from watching a program behave. An inference that hardened into an
    assumption is how a project gets stuck -- and how a wrong fact propagates
    into everyone who reads your notes.

    ## Your Task

    Cover: register file and widths, memory model (including whether spaces are
    disjoint), the opcode map, control flow and any paging, interrupts and their
    priority, timing and clocks, and peripherals.

    **Mark every statement.** Published fact, convention, or inference from
    observation. Cite the datasheet where you have one.

    Then give it to someone who has not worked on the target and ask them to use
    it. Record what they had to ask.

    ## Report

    The document, and the questions it failed to answer.
    """ + E)

lab(116, "Negative Results", readme="""
    ## Objective

    Find three things you ruled out, and write them up where the next person
    will look.

    ## Background

    Module 60 section 1. Bring-up is mostly eliminating plausible wrong answers.
    You will spend a day proving something is *not* the cause, feel like you
    achieved nothing, and move on -- and then someone else will spend the same
    day on the same wrong answer. So will you, in four months.

    The corpus does this well in places. `outrun` documents a ruled-out red
    herring. `tamarecomp`'s validation records two harness bugs that
    impersonated CPU bugs, including Windows text-mode stdout expanding `0x0A`
    into `0x0D 0x0A` -- caught because `X = 0x0A0D` is impossible for a 12-bit
    register.

    ## Your Task

    Go through your project's history and find three. At least one must be a
    **harness bug that impersonated a target bug** -- you will have one.

    For each: the symptom, what you suspected, how you ruled it out, and what it
    actually was. Include the giveaway if there was one.

    ## Report

    Three writeups, placed where someone hitting the same symptom would find
    them -- the `docs/` directory, not a personal notebook.

    ## Why This One Matters

    This is the single most under-supplied artifact in the field and the cheapest
    to produce. You already did the work.
    """ + E)

lab(117, "Unit 15 Capstone: Contribute Something Real", readme="""
    ## Objective

    Contribute something to a project you did not write.

    ## Your Task

    Pick one:

    - **An upstream fix** with a minimal reproducer and a regression test (Lab 109)
    - **A named gap filled** against an existing interface (Lab 110)
    - **A second game** on someone else's toolkit (Module 58 section 2)
    - **A feasibility report** that saves the next person the work (Lab 96)
    - **An artifact for a decomp project** they actually want (Lab 105)
    - **Documentation** for a toolkit that has none

    ## Deliverable

    The contribution, plus a writeup of what it took: how you found the work,
    how long the minimisation took, what the maintainer asked for, and what you
    would do differently.

    ## What Counts

    Merged is ideal. Rejected with a stated reason is a complete answer -- write
    up the reason. Ignored is a partial answer; say how long you waited and what
    you would try next.

    ## What Does Not Count

    A drive-by issue with no reproducer. A pull request that reformats someone's
    code. A feature request.

    ## The Point

    Module 60 section 8: this field's history is a series of people
    independently rediscovering the same things. The fix is generous, specific
    contribution -- and the unglamorous artifacts (traces, symbol files,
    feasibility reports, "this does not work and here is why") are cheap for you
    and expensive for everyone else to reproduce.
    """)

lab(118, "Measure an Open Problem", readme="""
    ## Objective

    Pick an open problem where the honest state is "nobody has counted", build
    the corpus and the measurement, and publish the number with its method.

    ## Background

    Module 61. Several of the problems there are open mainly because nobody has
    measured anything:

    - **How common is self-modifying code**, really, across a large corpus of
      ZX Spectrum or TI-83 programs? Nobody has published that number and the
      field's intuition may be badly wrong in either direction.
    - **How statically recompilable is a given ROM?** There is no accepted
      metric. `cybikorecomp`'s unresolved-transfer count before and after
      assembling the address space is the closest thing.
    - **Does pointer-scan hinting help or hurt**, measured across N targets
      rather than the one where it went wrong?

    ## Your Task

    Follow Module 62's method:

    1. Ask something that **can be answered no**.
    2. Build or identify the corpus, and identify it precisely (hashes, or a
       documented acquisition procedure).
    3. Build the measurement, and **prove it detects a bug you inject**.
    4. Measure. Vary one thing.
    5. Suspect the harness first.
    6. Report failures categorised and partials honestly.

    ## Report

    The number, the method, the corpus, and the code. Plus: what result would
    have made you abandon the hypothesis, and whether you got close to it.

    A measurement is a complete contribution and the cheapest kind to make.
    """ + E)

lab(120, "Design a Study", readme="""
    ## Objective

    Take one open problem from Module 61 and write it up as a study you could
    actually run.

    ## Your Task

    Produce a design covering:

    1. **The question, in falsifiable form.** Not "can X be recompiled" -- that
       has no failure condition. Something with a number at the end.
    2. **The corpus.** What, how many, how identified, how acquired -- and
       whether you can legally share it (Module 45).
    3. **The oracle.** What are you comparing against, and is it independent of
       your implementation? Module 62 section 2 grades this: strongest is
       somebody else's implementation in another language from the same primary
       source.
    4. **The success criterion**, stated before you run anything.
    5. **What you will vary, and what you will hold fixed.**
    6. **How you will validate the harness** -- which bug will you inject to
       prove the measurement works?
    7. **What result would make you abandon the hypothesis.**

    ## Report

    The design. You do not have to run it -- but it must be runnable by someone
    else without asking you anything.

    ## What Good Looks Like

    Point 7 is real. If you cannot describe a result that would change your mind,
    the question is not falsifiable and you should go back to point 1.
    """ + E)

lab(122, "Technique Writeup", readme="""
    ## Objective

    Take something you built in this course and write it up so someone else can
    reimplement it.

    ## Background

    Module 63 section 2. The structure that works:

    1. **The problem, concretely.** Not "indirect calls are hard" but "22,097
       functions, a call through a vtable slot, no target at compile time."
    2. **What you tried that did not work**, and why. The part readers cannot
       get anywhere else, and the part everyone omits.
    3. **The technique**, with enough detail to reimplement -- a code listing,
       not a description of one.
    4. **What it cost.** `xboxrecomp` does this well: binary search over 22,097
       entries is at most 15 comparisons, and *"at ~120 ICALLs per second, this
       is negligible overhead."* A technique without its cost is unusable.
    5. **Where it does not apply.**
    6. **The measurement**, with the method to re-derive it.

    ## Your Task

    Write it. Then **give it to someone who has not seen your code and ask them
    to reimplement from it.** Record every question they ask.

    ## Report

    The writeup, the questions it failed to answer, and the revision.

    ## Checklist Before Publishing

    - [ ] Does every number have a method attached?
    - [ ] Have you said what it does **not** establish?
    - [ ] Have you named what you tried that failed?
    - [ ] Have you credited prior work by name?
    - [ ] Is anything a "first" you cannot verify?
    """ + E)

lab(123, "Machine Document, Reviewed", readme="""
    ## Objective

    Write machine documentation for a target, then have it reviewed by someone
    who has not worked on it.

    ## Background

    This is Lab 115 with the review step made mandatory, and it is the last lab
    in the course for a reason: Module 60's argument is that writing things down
    where they will still be found is what stops this field rediscovering the
    same facts every few years.

    ## Your Task

    1. Write the document (Lab 115's scope), marking every statement as
       published fact, convention, or inference.
    2. **Have someone use it** who has not worked on the target -- to write a
       decoder, an emulator, or just to answer questions you pose.
    3. Record every question they had to ask you.
    4. Revise until the questions stop.
    5. Publish it where the platform's community already is (Module 63 section 5)
       -- not only in your own repository.

    ## Report

    The document, the review questions, the revisions, and where you published.

    ## The Standard

    Someone can use your notes to build something you did not build. If they
    still have to ask you, it is not documentation yet -- it is a reminder to
    yourself.
    """ + E)

report()
