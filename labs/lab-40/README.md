# Lab 40: Shader Translator Prototype

## Objective

Translate a simplified fixed-function combiner description (JSON format)
into a GLSL fragment shader. Many older consoles use fixed-function
texture combiners rather than programmable shaders. Recompilation projects
must translate these combiner configurations into modern shader code.

By the end of this lab you will be able to:

- Parse a JSON combiner description
- Generate valid GLSL fragment shader code
- Handle texture sampling, color combine modes, and alpha test

## Background

Before programmable shaders, GPUs used a fixed-function pipeline where
the developer configured "combiner stages" to blend textures and colors.
In a recomp project, we need to generate equivalent GLSL shaders at
runtime based on the game's combiner state.

### Combiner Description Format (JSON)

```json
{
    "textures": [0, 1],
    "color_mode": "modulate",
    "alpha_test": {"func": "greater", "ref": 0.5}
}
```

**Fields:**

- `textures`: list of texture unit indices to sample (0-7). Each gets a
  `uniform sampler2D` and a `texture()` call.
- `color_mode`: how to combine texture colors:
  - `"replace"` -- use the first texture color directly
  - `"modulate"` -- multiply all texture colors together
  - `"add"` -- add all texture colors (clamped to 1.0)
  - `"decal"` -- blend tex0 onto tex1 using tex0's alpha
- `alpha_test`: optional alpha test configuration:
  - `func`: `"greater"`, `"less"`, `"gequal"`, `"lequal"`, `"equal"`, `"never"`, `"always"`
  - `ref`: float reference value (0.0-1.0)
  - If omitted or null, no alpha test is applied.

### Output GLSL Structure

```glsl
#version 330 core
in vec2 v_texcoord;
uniform sampler2D u_tex0;
uniform sampler2D u_tex1;
out vec4 frag_color;
void main() {
    vec4 t0 = texture(u_tex0, v_texcoord);
    vec4 t1 = texture(u_tex1, v_texcoord);
    vec4 combined = t0 * t1;
    if (!(combined.a > 0.5)) discard;
    frag_color = combined;
}
```

## Files

| File                   | Description                          |
|------------------------|--------------------------------------|
| `shader_translate.py`  | Shader translator (starter code)    |
| `test_lab.py`           | Pytest test suite                   |

## Instructions

1. Open `shader_translate.py` and read the starter code.
2. Complete each function marked with a `TODO` comment.
3. Run the tests:
   ```
   python -m pytest test_lab.py -v
   ```

## References

- OpenGL 3.3 GLSL specification
- Fixed-function combiner documentation (various console SDKs)
