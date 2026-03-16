# Lab 41: TEV Stage Compiler

## Objective

Translate GameCube TEV (Texture Environment) stage configurations into GLSL
shader code. The GameCube's GPU (Flipper) uses a configurable multi-stage
TEV pipeline instead of programmable shaders. Recompilation projects must
convert these TEV configurations into equivalent GLSL.

By the end of this lab you will be able to:

- Parse TEV stage configuration data
- Understand the TEV color/alpha combiner math
- Generate GLSL code that replicates the TEV pipeline

## Background

The GameCube TEV unit supports up to 16 stages. Each stage computes:

```
result = d + ((1 - c) * a + c * b)     when op = "add"
result = d + ((a - b) * c)             when op = "sub"  (actually: d + a*c - b*c)
```

This is applied separately for the color (RGB) and alpha (A) channels.

### TEV Stage JSON Format

```json
{
    "stages": [
        {
            "color_inputs": {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "zero"},
            "color_op": "add",
            "alpha_inputs": {"a": "tex0_a", "b": "zero", "c": "zero", "d": "zero"},
            "alpha_op": "add"
        }
    ],
    "textures": [0, 1]
}
```

### Input Sources

| Source Name     | GLSL Expression       | Notes                    |
|-----------------|-----------------------|--------------------------|
| `zero`          | `vec3(0.0)` / `0.0`  | Constant zero            |
| `one`           | `vec3(1.0)` / `1.0`  | Constant one             |
| `half`          | `vec3(0.5)` / `0.5`  | Constant half            |
| `tex0_rgb`      | `t0.rgb`              | Texture 0 color          |
| `tex0_a`        | `t0.a`                | Texture 0 alpha          |
| `tex1_rgb`      | `t1.rgb`              | Texture 1 color          |
| `tex1_a`        | `t1.a`                | Texture 1 alpha          |
| `ras_rgb`       | `v_color.rgb`         | Rasterized vertex color  |
| `ras_a`         | `v_color.a`           | Rasterized vertex alpha  |
| `prev_rgb`      | `prev.rgb`            | Previous stage color     |
| `prev_a`        | `prev.a`              | Previous stage alpha     |

### Operators

- `add`: `result = d + mix(a, b, c)` which equals `d + ((1-c)*a + c*b)`
- `sub`: `result = d - mix(a, b, c)` which equals `d - ((1-c)*a + c*b)`

## Files

| File              | Description                           |
|-------------------|---------------------------------------|
| `tev_compiler.py` | TEV compiler (starter code)          |
| `test_lab.py`      | Pytest test suite                    |

## Instructions

1. Open `tev_compiler.py` and read the starter code.
2. Complete each function marked with a `TODO` comment.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## Expected Output (single-stage replace)

```glsl
#version 330 core
in vec2 v_texcoord;
in vec4 v_color;
uniform sampler2D u_tex0;
out vec4 frag_color;
void main() {
    vec4 t0 = texture(u_tex0, v_texcoord);
    vec4 prev = vec4(0.0);
    // TEV Stage 0
    prev.rgb = vec3(0.0) + mix(t0.rgb, vec3(0.0), vec3(0.0));
    prev.a = 0.0 + mix(t0.a, 0.0, 0.0);
    frag_color = clamp(prev, 0.0, 1.0);
}
```

## References

- libogc GX TEV documentation
- Dolphin Emulator shader generation source
- US Patent 6,664,962 (Nintendo TEV)
