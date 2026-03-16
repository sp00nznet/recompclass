"""
Tests for Lab 40: Shader Translator Prototype
"""

import json
import shader_translate as st


# ---------------------------------------------------------------------------
# Version directive
# ---------------------------------------------------------------------------

class TestEmitVersion:
    def test_version(self):
        assert st.emit_version() == "#version 330 core"


# ---------------------------------------------------------------------------
# Uniform declarations
# ---------------------------------------------------------------------------

class TestEmitTextureUniforms:
    def test_single(self):
        lines = st.emit_texture_uniforms([0])
        assert lines == ["uniform sampler2D u_tex0;"]

    def test_multiple(self):
        lines = st.emit_texture_uniforms([0, 1, 2])
        assert len(lines) == 3
        assert "u_tex0" in lines[0]
        assert "u_tex1" in lines[1]
        assert "u_tex2" in lines[2]

    def test_empty(self):
        lines = st.emit_texture_uniforms([])
        assert lines == []


# ---------------------------------------------------------------------------
# Texture sampling
# ---------------------------------------------------------------------------

class TestEmitTextureSamples:
    def test_single(self):
        lines = st.emit_texture_samples([0])
        assert len(lines) == 1
        assert "vec4 t0 = texture(u_tex0, v_texcoord);" in lines[0]

    def test_two(self):
        lines = st.emit_texture_samples([0, 1])
        assert len(lines) == 2
        assert "t0" in lines[0]
        assert "t1" in lines[1]


# ---------------------------------------------------------------------------
# Color combine
# ---------------------------------------------------------------------------

class TestEmitCombine:
    def test_replace(self):
        line = st.emit_combine([0], "replace")
        assert "combined = t0" in line
        assert "*" not in line

    def test_modulate_two(self):
        line = st.emit_combine([0, 1], "modulate")
        assert "t0 * t1" in line

    def test_modulate_three(self):
        line = st.emit_combine([0, 1, 2], "modulate")
        assert "t0 * t1 * t2" in line

    def test_add_two(self):
        line = st.emit_combine([0, 1], "add")
        assert "t0 + t1" in line
        assert "clamp" in line

    def test_decal(self):
        line = st.emit_combine([0, 1], "decal")
        assert "mix" in line
        assert "t0.a" in line

    def test_decal_single_fallback(self):
        # Only one texture -> fall back to replace
        line = st.emit_combine([0], "decal")
        assert "combined = t0" in line


# ---------------------------------------------------------------------------
# Alpha test
# ---------------------------------------------------------------------------

class TestEmitAlphaTest:
    def test_greater(self):
        line = st.emit_alpha_test({"func": "greater", "ref": 0.5})
        assert "discard" in line
        assert "combined.a > 0.5" in line

    def test_less(self):
        line = st.emit_alpha_test({"func": "less", "ref": 0.1})
        assert "combined.a < 0.1" in line
        assert "discard" in line

    def test_gequal(self):
        line = st.emit_alpha_test({"func": "gequal", "ref": 0.0})
        assert ">=" in line

    def test_never(self):
        line = st.emit_alpha_test({"func": "never", "ref": 0.0})
        assert "discard" in line
        # Should unconditionally discard
        assert "if" not in line

    def test_always(self):
        result = st.emit_alpha_test({"func": "always", "ref": 0.0})
        assert result is None

    def test_none(self):
        result = st.emit_alpha_test(None)
        assert result is None


# ---------------------------------------------------------------------------
# Full translation
# ---------------------------------------------------------------------------

class TestTranslate:
    def test_modulate_with_alpha(self):
        combiner = {
            "textures": [0, 1],
            "color_mode": "modulate",
            "alpha_test": {"func": "greater", "ref": 0.5},
        }
        glsl = st.translate(combiner)
        assert "#version 330 core" in glsl
        assert "uniform sampler2D u_tex0;" in glsl
        assert "uniform sampler2D u_tex1;" in glsl
        assert "in vec2 v_texcoord;" in glsl
        assert "out vec4 frag_color;" in glsl
        assert "void main()" in glsl
        assert "texture(u_tex0, v_texcoord)" in glsl
        assert "texture(u_tex1, v_texcoord)" in glsl
        assert "t0 * t1" in glsl
        assert "discard" in glsl
        assert "frag_color = combined;" in glsl

    def test_replace_no_alpha(self):
        combiner = {
            "textures": [0],
            "color_mode": "replace",
        }
        glsl = st.translate(combiner)
        assert "u_tex0" in glsl
        assert "u_tex1" not in glsl
        assert "discard" not in glsl
        assert "combined = t0" in glsl

    def test_add_mode(self):
        combiner = {
            "textures": [0, 1],
            "color_mode": "add",
            "alpha_test": None,
        }
        glsl = st.translate(combiner)
        assert "clamp" in glsl
        assert "t0 + t1" in glsl

    def test_json_round_trip(self):
        desc = json.dumps({
            "textures": [0],
            "color_mode": "replace",
        })
        glsl = st.translate_json(desc)
        assert "#version 330 core" in glsl
        assert "frag_color = combined;" in glsl

    def test_three_textures_modulate(self):
        combiner = {
            "textures": [0, 1, 2],
            "color_mode": "modulate",
        }
        glsl = st.translate(combiner)
        assert "u_tex2" in glsl
        assert "t0 * t1 * t2" in glsl
