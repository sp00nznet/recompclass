"""
Lab 40: Shader Translator Prototype

Translate a JSON combiner description into a GLSL fragment shader.
"""

import json


# ---------------------------------------------------------------------------
# Alpha-test comparison operators mapped to GLSL
# ---------------------------------------------------------------------------

ALPHA_FUNC_GLSL = {
    "greater": ">",
    "less":    "<",
    "gequal":  ">=",
    "lequal":  "<=",
    "equal":   "==",
    "never":   None,   # always discard
    "always":  None,   # never discard (no-op)
}


# ---------------------------------------------------------------------------
# Code-generation helpers -- complete the TODOs
# ---------------------------------------------------------------------------

def emit_version():
    """Return the GLSL version directive.

    Returns
    -------
    str
        '#version 330 core'
    """
    # TODO
    pass


def emit_texture_uniforms(texture_indices):
    """Emit uniform sampler2D declarations for each texture index.

    Parameters
    ----------
    texture_indices : list of int
        e.g. [0, 1] -> two uniform declarations.

    Returns
    -------
    list of str
        Each string is one line, e.g. 'uniform sampler2D u_tex0;'
    """
    # TODO: for each index, emit "uniform sampler2D u_tex<N>;"
    pass


def emit_texture_samples(texture_indices):
    """Emit texture sampling statements.

    Each texture is sampled into a local variable named t<N>.

    Returns
    -------
    list of str
        e.g. ['    vec4 t0 = texture(u_tex0, v_texcoord);']
    """
    # TODO: for each index, emit an indented sampling statement
    pass


def emit_combine(texture_indices, color_mode):
    """Emit the color combine statement.

    Parameters
    ----------
    texture_indices : list of int
    color_mode : str
        One of 'replace', 'modulate', 'add', 'decal'.

    Returns
    -------
    str
        An indented C statement like '    vec4 combined = t0 * t1;'

    Behavior by mode:
        replace  -> combined = t0
        modulate -> combined = t0 * t1 (* t2 * ... if more textures)
        add      -> combined = clamp(t0 + t1 (+ t2 ...), 0.0, 1.0)
        decal    -> combined = mix(t1, t0, t0.a)
                    (blend t0 onto t1 using t0's alpha; needs >= 2 textures,
                     if only 1 texture, fall back to replace)
    """
    # TODO: implement each color mode
    pass


def emit_alpha_test(alpha_test):
    """Emit an alpha test discard statement.

    Parameters
    ----------
    alpha_test : dict or None
        {"func": "greater", "ref": 0.5} or None.

    Returns
    -------
    str or None
        An indented discard statement, or None if no alpha test.

    For func == "never":  always discard -> '    discard;'
    For func == "always": no test needed -> return None
    For comparison funcs: '    if (!(combined.a > 0.5)) discard;'
    """
    # TODO: handle the alpha test cases
    pass


def translate(combiner):
    """Translate a combiner description dict into a GLSL fragment shader.

    Parameters
    ----------
    combiner : dict
        {
            "textures": [0, 1],
            "color_mode": "modulate",
            "alpha_test": {"func": "greater", "ref": 0.5}  // optional
        }

    Returns
    -------
    str
        Complete GLSL fragment shader source.
    """
    # TODO: assemble the shader by calling the helper functions above.
    #
    # Structure:
    #   1. Version directive
    #   2. 'in vec2 v_texcoord;'
    #   3. Texture uniform declarations
    #   4. 'out vec4 frag_color;'
    #   5. 'void main() {'
    #   6.     Texture samples
    #   7.     Combine statement
    #   8.     Alpha test (if present)
    #   9.     '    frag_color = combined;'
    #  10. '}'
    #
    # Join all lines with '\n' and return.
    pass


def translate_json(json_str):
    """Convenience: parse a JSON string and translate it.

    Parameters
    ----------
    json_str : str
        JSON-encoded combiner description.

    Returns
    -------
    str
        GLSL fragment shader source.
    """
    return translate(json.loads(json_str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = {
        "textures": [0, 1],
        "color_mode": "modulate",
        "alpha_test": {"func": "greater", "ref": 0.5},
    }
    print(translate(sample))
