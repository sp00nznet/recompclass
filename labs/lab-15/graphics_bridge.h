#ifndef GRAPHICS_BRIDGE_H
#define GRAPHICS_BRIDGE_H

#include <stdint.h>

/*
 * graphics_bridge.h -- Abstract graphics command interface.
 *
 * This header defines a platform-independent set of 2D draw commands.
 * The backend (graphics_bridge.c) translates these to real draw calls.
 */

/* RGBA color. */
typedef struct {
    uint8_t r, g, b, a;
} GfxColor;

/* Rectangle (position + size). */
typedef struct {
    int x, y, w, h;
} GfxRect;

/* Sprite handle (opaque identifier returned by texture loading). */
typedef uint32_t GfxSprite;

#define GFX_SPRITE_INVALID  ((GfxSprite)0)

/* ------------------------------------------------------------------ */
/*  Lifecycle                                                          */
/* ------------------------------------------------------------------ */

/*
 * Initialize the graphics backend.
 * Creates a window of the given dimensions.
 * Returns 0 on success, nonzero on failure.
 */
int gfx_init(const char *title, int width, int height);

/*
 * Shut down the graphics backend and release all resources.
 */
void gfx_shutdown(void);

/* ------------------------------------------------------------------ */
/*  Draw commands                                                      */
/* ------------------------------------------------------------------ */

/* Clear the screen to the given color. */
void gfx_cmd_clear(GfxColor color);

/* Draw a filled rectangle. */
void gfx_cmd_draw_rect(GfxRect rect, GfxColor color);

/*
 * Draw a sprite at the given position.
 * TODO: Implement texture loading and rendering.
 */
void gfx_cmd_draw_sprite(GfxSprite sprite, int x, int y);

/* Present the back buffer (flip/swap). */
void gfx_cmd_present(void);

/* ------------------------------------------------------------------ */
/*  Texture management (TODO)                                          */
/* ------------------------------------------------------------------ */

/* GfxSprite gfx_load_texture(const char *path); */
/* void gfx_free_texture(GfxSprite sprite);       */

#endif /* GRAPHICS_BRIDGE_H */
