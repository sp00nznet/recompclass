"""
Lab 41: TEV Stage Compiler

Translate GameCube TEV (Texture Environment) stage configurations into GLSL.
"""

import json


# ---------------------------------------------------------------------------
# Input source mapping
# ---------------------------------------------------------------------------

# Maps TEV input names to GLSL expressions.
# Color (vec3) sources:
COLOR_SOURCES = {
    "zero":     "vec3(0.0)",
    "one":      "vec3(1.0)",
    "half":     "vec3(0.5)",
    "tex0_rgb": "t0.rgb",
    "tex1_rgb": "t1.rgb",
    "ras_rgb":  "v_color.rgb",
    "prev_rgb": "prev.rgb",
}

# Alpha (float) sources:
ALPHA_SOURCES = {
    "zero":    "0.0",
    "one":     "1.0",
    "half":    "0.5",
    "tex0_a":  "t0.a",
    "tex1_a":  "t1.a",
    "ras_a":   "v_color.a",
    "prev_a":  "prev.a",
}


# ---------------------------------------------------------------------------
# Code generation helpers -- complete the TODOs
# ---------------------------------------------------------------------------

def resolve_color_input(name):
    """Resolve a color input name to its GLSL expression.

    Parameters
    ----------
    name : str
        A key from COLOR_SOURCES.

    Returns
    -------
    str
        The corresponding GLSL expression.

    Raises
    ------
    ValueError
        If the name is not recognized.
    """
    # TODO: look up name in COLOR_SOURCES, raise ValueError if missing
    pass


def resolve_alpha_input(name):
    """Resolve an alpha input name to its GLSL expression.

    Parameters
    ----------
    name : str
        A key from ALPHA_SOURCES.

    Returns
    -------
    str
        The corresponding GLSL expression.

    Raises
    ------
    ValueError
        If the name is not recognized.
    """
    # TODO: look up name in ALPHA_SOURCES, raise ValueError if missing
    pass


def emit_tev_color(stage_idx, inputs, op):
    """Emit the GLSL statement for one TEV stage's color calculation.

    Parameters
    ----------
    stage_idx : int
        Stage number (for the comment).
    inputs : dict
        {"a": str, "b": str, "c": str, "d": str} -- input source names.
    op : str
        "add" or "sub".

    Returns
    -------
    str
        Indented GLSL statement like:
        '    prev.rgb = d + mix(a, b, c);'    (for op "add")
        '    prev.rgb = d - mix(a, b, c);'    (for op "sub")

    The mix() function in GLSL computes: mix(x, y, a) = x*(1-a) + y*a
    which matches the TEV formula: (1-c)*a + c*b = mix(a, b, c).
    """
    # TODO: resolve each input (a, b, c, d) using resolve_color_input,
    # then build the GLSL statement.
    pass


def emit_tev_alpha(stage_idx, inputs, op):
    """Emit the GLSL statement for one TEV stage's alpha calculation.

    Same formula as color but with float values instead of vec3.

    Returns
    -------
    str
        Indented GLSL statement like:
        '    prev.a = d + mix(a, b, c);'
    """
    # TODO: same as emit_tev_color but using resolve_alpha_input
    pass


def emit_stage(stage_idx, stage):
    """Emit all GLSL lines for one TEV stage.

    Parameters
    ----------
    stage_idx : int
        Stage number.
    stage : dict
        {
            "color_inputs": {"a": ..., "b": ..., "c": ..., "d": ...},
            "color_op": "add" or "sub",
            "alpha_inputs": {"a": ..., "b": ..., "c": ..., "d": ...},
            "alpha_op": "add" or "sub"
        }

    Returns
    -------
    list of str
        Lines of GLSL code for this stage (including comment header).
    """
    # TODO: return a list containing:
    #   - A comment line: "    // TEV Stage <N>"
    #   - The color calculation line
    #   - The alpha calculation line
    pass


def compile_tev(config):
    """Compile a TEV configuration into a complete GLSL fragment shader.

    Parameters
    ----------
    config : dict
        {
            "stages": [ ... ],
            "textures": [0, 1, ...]
        }

    Returns
    -------
    str
        Complete GLSL fragment shader source.
    """
    # TODO: assemble the full shader:
    #
    # 1. '#version 330 core'
    # 2. 'in vec2 v_texcoord;'
    # 3. 'in vec4 v_color;'
    # 4. Uniform declarations for each texture
    # 5. 'out vec4 frag_color;'
    # 6. 'void main() {'
    # 7.     Texture sampling statements
    # 8.     '    vec4 prev = vec4(0.0);'
    # 9.     For each stage: emit_stage()
    # 10.    '    frag_color = clamp(prev, 0.0, 1.0);'
    # 11. '}'
    #
    # Join with '\n' and return.
    pass


def compile_tev_json(json_str):
    """Convenience: parse JSON string and compile."""
    return compile_tev(json.loads(json_str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = {
        "stages": [
            {
                "color_inputs": {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "zero"},
                "color_op": "add",
                "alpha_inputs": {"a": "tex0_a", "b": "zero", "c": "zero", "d": "zero"},
                "alpha_op": "add",
            },
        ],
        "textures": [0],
    }
    print(compile_tev(sample))
