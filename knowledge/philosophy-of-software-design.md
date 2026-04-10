# A Philosophy of Software Design — Reference Guide

*Based on the book by John Ousterhout (Stanford University)*

This is a condensed reference of the key principles, intended to inform code review, design decisions, and software architecture guidance.

---

## The Central Thesis

**The greatest limitation in software is our ability to understand the systems we build.** The primary goal of software design is to reduce complexity. Every design decision should be evaluated by asking: *does this make the system simpler or more complex?*

---

## Chapter 1: The Nature of Complexity

### What Complexity Is

Complexity is anything related to the structure of a system that makes it hard to understand and modify. It is not about the size of the system — a large system can be simple, and a small system can be complex.

### Ousterhout's Definition

> Complexity is determined by the activities that are most common. If a system has a few parts that are very complicated but those parts almost never need to be touched, they don't have much impact on overall complexity.

### Three Manifestations of Complexity

1. **Change amplification** — A simple change requires modifications in many places. Example: if a color appears as a literal in many places, changing it means editing every occurrence.

2. **Cognitive load** — How much a developer needs to know to complete a task. More state, more dependencies, more special cases = higher cognitive load. Note: sometimes more lines of code can *reduce* cognitive load if the code is clearer.

3. **Unknown unknowns** — The worst form. It's not obvious what code needs to change, or what information you need to complete a task. The developer doesn't even know what they don't know.

### Causes of Complexity

Complexity is caused by two things:
- **Dependencies** — when code cannot be understood or modified in isolation
- **Obscurity** — when important information is not obvious

Complexity is **incremental**. It doesn't come from one catastrophic decision but from hundreds of small choices. "Just this one time" accumulates into an incomprehensible system.

---

## Chapter 2: Strategic vs. Tactical Programming

### Tactical Programming (the problem)

The tactical mindset is: *get the feature working as fast as possible*. Each shortcut is small, but they compound. Tactical programming produces spaghetti code. Tactical tornados — programmers who ship fast but leave destruction — are the most damaging members of a team.

### Strategic Programming (the solution)

The strategic mindset is: *produce a great design that also happens to work*. The primary goal is a clean design; working code is a given.

**Investment mindset**: spend 10-20% of development time on design improvements. This is not wasted time — it pays back rapidly through reduced future complexity.

### Key Insight

> The best way to lower development costs is to hire great designers, not more programmers.

---

## Chapter 3: Deep Modules

This is the most important chapter in the book.

### Modules

A module is any unit with an interface and an implementation: a class, a function, a service, a subsystem. Every module has:
- **Interface** — what users of the module need to know
- **Implementation** — the code that carries out the promises of the interface

### Deep vs. Shallow Modules

Think of a module as a rectangle:
- **Width** = complexity of the interface
- **Height** = functionality provided

**Deep modules** have simple interfaces but provide powerful functionality. They hide enormous complexity behind a small surface area.

**Shallow modules** have complex interfaces relative to the functionality they provide. They don't hide much — the user has to understand nearly as much as the implementer.

### Examples of Deep Modules

- **Unix file I/O**: `open()`, `read()`, `write()`, `close()`, `lseek()` — five calls that hide disk drivers, block caching, directory management, permissions, journaling, etc.
- **Garbage collectors**: no interface at all — just works invisibly
- **TCP/IP**: a simple reliable byte stream hides packet loss, retransmission, congestion control, routing

### Examples of Shallow Modules

- A `LinkedList` class that provides no functionality beyond what an array gives, with a more complex interface
- Java's `FileInputStream` / `BufferedInputStream` / `InputStreamReader` stack — three classes to read a file, each adding trivial functionality with a new interface

### The Rule

> The best modules are those whose interfaces are much simpler than their implementations.

---

## Chapter 4: Information Hiding (and Leakage)

### Information Hiding

The most important technique for achieving deep modules. Each module should encapsulate knowledge about its design decisions, embedding it in the implementation without appearing in the interface.

Information hiding reduces complexity in two ways:
1. Simplifies the interface
2. Makes it easier to evolve the system (hidden information can change without affecting other modules)

### Information Leakage

The opposite of information hiding. Occurs when a design decision is reflected in multiple modules. If a change to that decision requires modifying multiple modules, that's leakage.

**Temporal decomposition** is a common cause: structuring code around the order in which operations happen, rather than around information hiding. Example: separate classes for reading and writing a file format both need to know the format — the format knowledge leaks across both.

### Fix for Information Leakage

Bring the related pieces together. If two classes both know about a file format, merge them into one class, or extract the shared knowledge into a single place.

---

## Chapter 5: General-Purpose Modules are Deeper

### The Tension

When designing a module, should it be general-purpose or special-purpose?

### Ousterhout's Answer

**Somewhat general-purpose.** The module's *functionality* should reflect current needs, but the *interface* should be general enough to support multiple uses.

### Questions to Ask

- What is the simplest interface that will cover all my current needs?
- In how many situations will this method be used?
- Is this API easy to use for my current needs?

### Example

Bad (special-purpose):
```
text.backspace(cursor)  // deletes char before cursor
text.delete(cursor)     // deletes char after cursor
```

Good (general-purpose):
```
text.insert(position, string)
text.delete(start, end)
```

The general-purpose version is *simpler* (fewer methods), *deeper* (handles more cases), and *easier to use*.

---

## Chapter 6: Different Layer, Different Abstraction

### The Principle

Each layer in a system should provide a different abstraction from the layers above and below it. If adjacent layers have similar abstractions, that's a red flag — something is wrong with the class decomposition.

### Pass-Through Methods

A method that does little except invoke another method with a similar signature. This is a red flag — it means the class decomposition is wrong.

**Fix options:**
- Expose the lower-level class directly
- Redistribute functionality between classes
- Merge the classes

### Pass-Through Variables

Variables passed through a long chain of methods that don't use them, just to reach a deeply nested method. This adds complexity everywhere in the chain.

**Fix options:**
- Shared context object
- Global variable (if truly global)
- Restructure to reduce the depth

---

## Chapter 7: Pull Complexity Downwards

### The Principle

When there's complexity that must exist somewhere, put it in the *implementation*, not in the *interface*. It's better for the module developer to suffer than for the module users to suffer, because:
- There are many users and one implementer
- The implementer already understands the context

### Example

Configuration parameters are a form of **pushing complexity up**. Every config parameter is a decision that wasn't made by the module developer — forcing users to figure it out. Ask: *will users or external tools be able to determine a better value than a hard-coded default?* If not, compute it internally.

### The Warning

Don't take this too far. If the information is naturally outside the module, pulling it in just creates information leakage in the other direction.

---

## Chapter 8: Better Together or Better Apart?

### When to Combine

- Pieces share information (e.g., same data format knowledge)
- Pieces are always used together
- Pieces overlap conceptually
- Combining simplifies the interface

### When to Separate

- Pieces are truly unrelated
- Separating simplifies the interface of each piece
- Separating eliminates duplication in the combined module

### Method Length

Ousterhout explicitly disagrees with the common advice that methods should be short (e.g., under 20 lines). **Length is not the problem — abstraction is.** A long method with a clean abstraction is better than many tiny methods that obscure the flow.

> If a method is split into pieces, the reader must read all the pieces and mentally reassemble them to understand the original method. If the pieces are only called from one place, this is a net loss.

### Conjoined Methods

Methods that cannot be understood independently (you must read A to understand B and vice versa). This is a red flag even when each method is short.

---

## Chapter 9: Define Errors Out of Existence

### The Problem

Exception handling is one of the worst sources of complexity. Programmers define too many error conditions, and handling code is often buggy because it's rarely exercised.

### The Solution: Define Errors Away

Restructure the API so the error condition cannot occur.

**Example — file deletion:**
- Windows: deleting an open file is an error (caller must handle it)
- Unix: deleting an open file succeeds — the file is unlinked from the directory but remains accessible to processes that have it open. The error is defined out of existence.

**Example — substring:**
- If `start` or `end` is out of range, don't throw — just clamp to the string boundaries and return the overlapping portion.

### Other Techniques

- **Mask exceptions** — handle them at a low level so callers never see them. TCP retransmits lost packets; callers see a reliable stream.
- **Exception aggregation** — handle many exceptions at one point rather than many handlers scattered throughout.
- **Just crash** — for truly exceptional errors (out of memory, corrupted data), don't try to recover. Crash and restart cleanly.

---

## Chapter 10: Design It Twice

Before settling on a design, **consider at least two alternatives.** Even if the first idea seems good, the comparison will deepen your understanding of the problem.

For each alternative, list pros and cons. Consider:
- Does it have a simpler interface?
- Does it provide a deeper abstraction?
- Is it more general-purpose?
- Will it be more or less efficient?

> If the best design is not immediately obvious, consider deferring the design decision until you have more information. But don't use this as an excuse for tactical programming.

---

## Chapter 11: Why Write Comments

### The Myth

"Good code is self-documenting" is used as an excuse not to write comments. Ousterhout disagrees.

### Why Comments Matter

- Code cannot fully convey the **rationale** behind design decisions
- Code cannot explain the designer's **mental model** — the high-level concept behind the module
- Comments capture information that cannot be expressed in code: why a decision was made, what a module's abstraction is, what the contract with callers is

### The Cost of No Comments

Without comments, developers must read the code to extract the abstraction. This is slow, error-prone, and defeats the purpose of abstraction.

---

## Chapter 12: Comments Should Describe Things That Are Not Obvious from the Code

### Categories of Comments

1. **Interface comments** — describe *what* (the abstraction), not *how* (the implementation). This is the most important kind.
2. **Implementation comments** — explain *why* the code does what it does, especially non-obvious logic.
3. **Cross-module comments** — describe dependencies between modules that aren't obvious from individual modules.

### Bad Comments

- Repeating the code in English: `// increment i` for `i++`
- Using the same words as the variable/function name: `// the current index` for `currentIndex`

### Good Comments

- Describe the abstraction the module provides
- State preconditions, postconditions, side effects
- Explain *why*, not *what*
- Document non-obvious consequences and edge cases

### Write Comments First

Write comments *before* writing code. This is a design tool — if you can't describe a clean interface in comments, the design is probably wrong.

---

## Chapter 13: Choosing Names

### The Principles

- **Create an image** — a name should evoke a mental picture of the thing. `height` is better than `y` for a vertical dimension.
- **Be precise** — vague names like `data`, `info`, `result`, `handle`, `tmp` indicate lazy thinking. What *kind* of data?
- **Be consistent** — use the same name for the same concept everywhere. Don't alternate between `length`, `size`, `count`, and `numItems`.
- **Avoid extra words** — `fileObject` vs `file` — if there's only one kind of file entity, just say `file`.

### Warning Signs

If it's hard to name something, it may be a sign that the design is unclear. Fix the design, not just the name.

---

## Chapter 14: Modifying Existing Code

### Tactical vs. Strategic When Modifying

Resist the temptation to make minimal tactical changes. When you modify code, **leave it cleaner than you found it.** Invest a little extra to improve the design of the area you're touching.

### Maintaining the Design

Each modification must be consistent with the original design abstraction. If the modification doesn't fit, the design needs to evolve — don't just hack it in.

### Comments Stay Current

When you change code, **update the comments.** Stale comments are worse than no comments — they actively mislead.

---

## Chapter 15: Consistency

Use consistent patterns throughout the codebase:

- **Names** — same concept, same name, everywhere
- **Coding style** — consistent formatting, conventions, idioms
- **Interfaces** — similar modules should have similar interfaces
- **Design patterns** — use established patterns consistently when applicable

### Enforcing Consistency

- Documentation (conventions guide)
- Automated tools (linters, formatters)
- Code review (the most important tool — humans catch consistency violations that tools miss)

> Don't change established conventions. The value of consistency comes from its universality. Even if you think your convention is better, the cost of inconsistency is worse than the benefit of a slightly better convention.

---

## Chapter 16: Software Trends Evaluated

Ousterhout evaluates popular trends through his complexity lens:

### Object-Oriented Programming
- **Good**: information hiding via private members, encapsulation
- **Bad**: inheritance creates deep dependencies between classes. Prefer composition. Keep class hierarchies shallow.

### Agile Development
- **Good**: incremental development, working software over documentation
- **Bad**: tactical mindset risk — sprints pressure teams toward tactical programming

### Unit Tests
- **Good**: facilitate refactoring, catch regressions
- **Bad**: obsessive testing of trivial code wastes time. Focus tests on tricky edge cases and non-obvious behavior.

### Test-Driven Development
- **Bad tendency**: focuses on getting features working rather than on good design. Design should come first; tests verify the design works.

### Design Patterns
- **Good**: when applied to problems they actually solve
- **Bad**: when applied because "we should use patterns." Don't force a pattern where it adds complexity.

---

## Chapter 17: Performance

### When to Optimize

- Design around critical paths from the start
- Measure before optimizing — intuition about performance is usually wrong
- Fundamental structural changes are easier to make early

### How to Think About Performance

- Simplify: reduce special cases, eliminate extra layers
- The best performance optimization is often a simpler design

---

## Key Maxims (Summary)

1. **Complexity is incremental** — death by a thousand cuts
2. **Working code is not enough** — design matters
3. **Make modules deep** — simple interface, powerful functionality
4. **Hide information** — encapsulate design decisions
5. **General-purpose interfaces are simpler** than special-purpose ones
6. **Different layers should have different abstractions**
7. **Pull complexity down** — handle it in the implementation, not the interface
8. **Define errors out of existence** — reduce exception handling
9. **Design it twice** — always consider alternatives
10. **Write comments first** — they are a design tool
11. **Choose names carefully** — names are a form of abstraction
12. **Be strategic, not tactical** — invest 10-20% in design
13. **Consistency reduces cognitive load** — be boringly consistent

---

## Red Flags Checklist

Use these to evaluate code during review:

| Red Flag | Symptom |
|---|---|
| Shallow module | Interface is nearly as complex as implementation |
| Information leakage | Same design decision appears in multiple modules |
| Temporal decomposition | Structure mirrors execution order rather than information hiding |
| Overexposure | API exposes internal state that callers shouldn't need |
| Pass-through method | Method does nothing but delegate to another with similar signature |
| Repetition | Same code appears in multiple places |
| Special-general mixture | General-purpose mechanism contains special-case code |
| Conjoined methods | Two methods that can't be understood independently |
| Comment repeats code | Comment says exactly what the code says |
| Vague name | Name doesn't convey specific meaning |
| Hard to pick a name | Design may be unclear |
| Hard to describe | Interface comment is convoluted — simplify the design |
| Nonobvious code | Behavior or intent can't be understood quickly |

---

*This reference is a condensed guide to the key principles. For the full treatment with examples and nuance, read the book: "A Philosophy of Software Design" by John Ousterhout, 2nd Edition.*
