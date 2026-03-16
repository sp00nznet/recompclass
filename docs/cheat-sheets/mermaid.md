# Mermaid Diagram Cheat Sheet for Course Contributors

## Flowchart Syntax (Most Used)

```mermaid
flowchart TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

Node shapes:
- `A[Text]` -- rectangle
- `A(Text)` -- rounded rectangle
- `A{Text}` -- diamond (decision)
- `A([Text])` -- stadium / pill
- `A[[Text]]` -- subroutine
- `A[(Text)]` -- cylinder (database)

Direction keywords: `TD` (top-down), `LR` (left-right), `BT` (bottom-top), `RL` (right-left)

Arrow types:
- `-->` solid arrow
- `-.->` dotted arrow
- `==>` thick arrow
- `-->|label|` labeled arrow

## Sequence Diagram Syntax

```mermaid
sequenceDiagram
    participant L as Loader
    participant D as Disassembler
    participant E as Emitter

    L->>D: Raw bytes
    D->>D: Decode instructions
    D->>E: IR stream
    E->>E: Generate C code
    Note over D,E: Core recompilation pipeline
```

Key elements:
- `participant` / `actor` -- define participants
- `->>` solid arrow, `-->>` dashed arrow
- `Note over A,B: text` -- spanning note
- `loop` / `alt` / `opt` -- control blocks

## Block Diagram Syntax

```mermaid
block-beta
    columns 3
    A["Input Binary"]:1
    B["Decoder"]:1
    C["Output C"]:1
    A --> B --> C
```

## Course Color Scheme

| Color                  | Hex       | Usage                    |
|------------------------|-----------|--------------------------|
| Blue                   | `#4A90D9` | Pipeline stages          |
| Green                  | `#27AE60` | Hardware components      |
| Orange                 | `#F39C12` | Decision points          |
| Red                    | `#E74C3C` | Challenges / problems    |

## Style Declarations for Consistent Theming

### Applying Styles to Individual Nodes

```mermaid
flowchart LR
    A[Load Binary]:::pipeline --> B{Valid Format?}:::decision
    B -->|Yes| C[Decode]:::pipeline
    B -->|No| D[Error]:::problem
    C --> E[CPU]:::hardware

    classDef pipeline fill:#4A90D9,stroke:#2C6FAC,color:#fff
    classDef hardware fill:#27AE60,stroke:#1E8449,color:#fff
    classDef decision fill:#F39C12,stroke:#D68910,color:#fff
    classDef problem fill:#E74C3C,stroke:#C0392B,color:#fff
```

### Applying Styles via `style` Keyword

```
style A fill:#4A90D9,stroke:#2C6FAC,color:#fff
```

### Subgraph Styling

```mermaid
flowchart TD
    subgraph pipeline["Recompilation Pipeline"]
        A[Parse] --> B[Decode] --> C[Emit]
    end
    style pipeline fill:#EAF2FA,stroke:#4A90D9
```

## GitHub Rendering Notes and Limitations

- GitHub renders Mermaid in fenced code blocks tagged with `mermaid`.
- Maximum diagram complexity is limited -- very large graphs may fail to render. Keep node count under ~100.
- `block-beta` diagrams may not render on older GitHub versions. Flowcharts are the safest choice.
- GitHub does not support `click` callbacks or interactive features.
- Font and spacing differ between GitHub light and dark themes -- avoid relying on precise layout.
- Inline HTML inside node labels is not supported on GitHub.
- If a diagram fails silently, check for special characters in labels (use quotes around labels with parentheses or brackets).

## Common Patterns Used in the Course

### Recompilation Pipeline (Horizontal)

```mermaid
flowchart LR
    A[Binary File]:::pipeline --> B[Loader]:::pipeline
    B --> C[Disassembler]:::pipeline
    C --> D[IR Builder]:::pipeline
    D --> E[Code Emitter]:::pipeline
    E --> F[C Source Output]:::pipeline

    classDef pipeline fill:#4A90D9,stroke:#2C6FAC,color:#fff
```

### Decision Tree (Format Detection)

```mermaid
flowchart TD
    A[Read Magic Bytes]:::pipeline --> B{0x4D5A?}:::decision
    B -->|Yes| C{PE Signature?}:::decision
    B -->|No| D{0x7F454C46?}:::decision
    C -->|Yes| E[PE / Windows]:::hardware
    C -->|No| F[MZ / DOS]:::hardware
    D -->|Yes| G[ELF]:::hardware
    D -->|No| H[Check other formats]:::problem

    classDef pipeline fill:#4A90D9,stroke:#2C6FAC,color:#fff
    classDef hardware fill:#27AE60,stroke:#1E8449,color:#fff
    classDef decision fill:#F39C12,stroke:#D68910,color:#fff
    classDef problem fill:#E74C3C,stroke:#C0392B,color:#fff
```

### Architecture Block Diagram

```mermaid
flowchart TD
    subgraph hw["Target Hardware"]
        CPU:::hardware
        MEM[Memory Map]:::hardware
        IO[I/O Registers]:::hardware
    end
    subgraph sw["Recompiled Output"]
        FUNC[C Functions]:::pipeline
        STUB[HW Stubs]:::pipeline
        MAIN[Main Loop]:::pipeline
    end
    CPU -.-> FUNC
    MEM -.-> STUB
    IO -.-> STUB
    MAIN --> FUNC
    MAIN --> STUB

    classDef pipeline fill:#4A90D9,stroke:#2C6FAC,color:#fff
    classDef hardware fill:#27AE60,stroke:#1E8449,color:#fff
```
