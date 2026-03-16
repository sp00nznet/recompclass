"""
Tests for Lab 41: TEV Stage Compiler
"""

import pytest
import tev_compiler as tev


# ---------------------------------------------------------------------------
# Input resolution
# ---------------------------------------------------------------------------

class TestResolveColorInput:
    def test_zero(self):
        assert tev.resolve_color_input("zero") == "vec3(0.0)"

    def test_tex0(self):
        assert tev.resolve_color_input("tex0_rgb") == "t0.rgb"

    def test_prev(self):
        assert tev.resolve_color_input("prev_rgb") == "prev.rgb"

    def test_unknown(self):
        with pytest.raises(ValueError):
            tev.resolve_color_input("nonexistent")


class TestResolveAlphaInput:
    def test_zero(self):
        assert tev.resolve_alpha_input("zero") == "0.0"

    def test_tex1_a(self):
        assert tev.resolve_alpha_input("tex1_a") == "t1.a"

    def test_unknown(self):
        with pytest.raises(ValueError):
            tev.resolve_alpha_input("nonexistent")


# ---------------------------------------------------------------------------
# Color/alpha statement emission
# ---------------------------------------------------------------------------

class TestEmitTevColor:
    def test_simple_replace(self):
        inputs = {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "zero"}
        line = tev.emit_tev_color(0, inputs, "add")
        assert "prev.rgb" in line
        assert "mix" in line
        assert "t0.rgb" in line

    def test_sub(self):
        inputs = {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "prev_rgb"}
        line = tev.emit_tev_color(0, inputs, "sub")
        assert " - mix(" in line

    def test_add(self):
        inputs = {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "prev_rgb"}
        line = tev.emit_tev_color(0, inputs, "add")
        assert " + mix(" in line


class TestEmitTevAlpha:
    def test_simple(self):
        inputs = {"a": "tex0_a", "b": "zero", "c": "zero", "d": "zero"}
        line = tev.emit_tev_alpha(0, inputs, "add")
        assert "prev.a" in line
        assert "t0.a" in line


# ---------------------------------------------------------------------------
# Stage emission
# ---------------------------------------------------------------------------

class TestEmitStage:
    def test_stage_lines(self):
        stage = {
            "color_inputs": {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "zero"},
            "color_op": "add",
            "alpha_inputs": {"a": "tex0_a", "b": "zero", "c": "zero", "d": "zero"},
            "alpha_op": "add",
        }
        lines = tev.emit_stage(0, stage)
        assert len(lines) == 3
        assert "TEV Stage 0" in lines[0]
        assert "prev.rgb" in lines[1]
        assert "prev.a" in lines[2]


# ---------------------------------------------------------------------------
# Full compilation
# ---------------------------------------------------------------------------

class TestCompileTev:
    def test_single_stage_replace(self):
        config = {
            "stages": [
                {
                    "color_inputs": {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "zero"},
                    "color_op": "add",
                    "alpha_inputs": {"a": "tex0_a", "b": "zero", "c": "zero", "d": "zero"},
                    "alpha_op": "add",
                }
            ],
            "textures": [0],
        }
        glsl = tev.compile_tev(config)
        assert "#version 330 core" in glsl
        assert "in vec2 v_texcoord;" in glsl
        assert "in vec4 v_color;" in glsl
        assert "uniform sampler2D u_tex0;" in glsl
        assert "out vec4 frag_color;" in glsl
        assert "void main()" in glsl
        assert "vec4 t0 = texture(u_tex0, v_texcoord);" in glsl
        assert "vec4 prev = vec4(0.0);" in glsl
        assert "TEV Stage 0" in glsl
        assert "frag_color = clamp(prev, 0.0, 1.0);" in glsl

    def test_two_stages(self):
        config = {
            "stages": [
                {
                    "color_inputs": {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "zero"},
                    "color_op": "add",
                    "alpha_inputs": {"a": "one", "b": "zero", "c": "zero", "d": "zero"},
                    "alpha_op": "add",
                },
                {
                    "color_inputs": {"a": "prev_rgb", "b": "tex1_rgb", "c": "half", "d": "zero"},
                    "color_op": "add",
                    "alpha_inputs": {"a": "prev_a", "b": "zero", "c": "zero", "d": "zero"},
                    "alpha_op": "add",
                },
            ],
            "textures": [0, 1],
        }
        glsl = tev.compile_tev(config)
        assert "TEV Stage 0" in glsl
        assert "TEV Stage 1" in glsl
        assert "u_tex0" in glsl
        assert "u_tex1" in glsl

    def test_two_textures(self):
        config = {
            "stages": [
                {
                    "color_inputs": {"a": "tex0_rgb", "b": "tex1_rgb", "c": "ras_rgb", "d": "zero"},
                    "color_op": "add",
                    "alpha_inputs": {"a": "tex0_a", "b": "zero", "c": "zero", "d": "zero"},
                    "alpha_op": "add",
                }
            ],
            "textures": [0, 1],
        }
        glsl = tev.compile_tev(config)
        assert "t0" in glsl
        assert "t1" in glsl
        assert "v_color.rgb" in glsl

    def test_sub_operation(self):
        config = {
            "stages": [
                {
                    "color_inputs": {"a": "tex0_rgb", "b": "zero", "c": "zero", "d": "one"},
                    "color_op": "sub",
                    "alpha_inputs": {"a": "one", "b": "zero", "c": "zero", "d": "zero"},
                    "alpha_op": "add",
                }
            ],
            "textures": [0],
        }
        glsl = tev.compile_tev(config)
        assert " - mix(" in glsl

    def test_no_textures(self):
        config = {
            "stages": [
                {
                    "color_inputs": {"a": "ras_rgb", "b": "zero", "c": "zero", "d": "zero"},
                    "color_op": "add",
                    "alpha_inputs": {"a": "ras_a", "b": "zero", "c": "zero", "d": "zero"},
                    "alpha_op": "add",
                }
            ],
            "textures": [],
        }
        glsl = tev.compile_tev(config)
        assert "sampler2D" not in glsl
        assert "v_color" in glsl
