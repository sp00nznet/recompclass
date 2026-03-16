#include "graphics_bridge.h"

#include <stdio.h>
#include <SDL2/SDL.h>

/*
 * graphics_bridge.c -- SDL2 backend for the abstract graphics bridge.
 *
 * This file translates the abstract draw commands defined in
 * graphics_bridge.h into SDL2 renderer calls.
 */

/* ------------------------------------------------------------------ */
/*  Internal state                                                     */
/* ------------------------------------------------------------------ */

static SDL_Window   *g_window   = NULL;
static SDL_Renderer *g_renderer = NULL;

/* ------------------------------------------------------------------ */
/*  Lifecycle                                                          */
/* ------------------------------------------------------------------ */

int gfx_init(const char *title, int width, int height)
{
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "[gfx] SDL_Init failed: %s\n", SDL_GetError());
        return -1;
    }

    g_window = SDL_CreateWindow(
        title,
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        width, height,
        SDL_WINDOW_SHOWN
    );
    if (!g_window) {
        fprintf(stderr, "[gfx] SDL_CreateWindow failed: %s\n", SDL_GetError());
        SDL_Quit();
        return -1;
    }

    g_renderer = SDL_CreateRenderer(
        g_window, -1,
        SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    );
    if (!g_renderer) {
        fprintf(stderr, "[gfx] SDL_CreateRenderer failed: %s\n", SDL_GetError());
        SDL_DestroyWindow(g_window);
        SDL_Quit();
        return -1;
    }

    printf("[gfx] Initialized %dx%d window.\n", width, height);
    return 0;
}

void gfx_shutdown(void)
{
    if (g_renderer) {
        SDL_DestroyRenderer(g_renderer);
        g_renderer = NULL;
    }
    if (g_window) {
        SDL_DestroyWindow(g_window);
        g_window = NULL;
    }
    SDL_Quit();
    printf("[gfx] Shut down.\n");
}

/* ------------------------------------------------------------------ */
/*  Draw commands                                                      */
/* ------------------------------------------------------------------ */

void gfx_cmd_clear(GfxColor color)
{
    SDL_SetRenderDrawColor(g_renderer, color.r, color.g, color.b, color.a);
    SDL_RenderClear(g_renderer);
}

void gfx_cmd_draw_rect(GfxRect rect, GfxColor color)
{
    SDL_Rect sdl_rect = { rect.x, rect.y, rect.w, rect.h };
    SDL_SetRenderDrawColor(g_renderer, color.r, color.g, color.b, color.a);
    SDL_RenderFillRect(g_renderer, &sdl_rect);
}

void gfx_cmd_draw_sprite(GfxSprite sprite, int x, int y)
{
    /*
     * TODO: Implement texture-based sprite rendering.
     *
     * Steps to implement:
     * 1. Maintain an internal array/map of GfxSprite -> SDL_Texture*.
     * 2. In gfx_load_texture(), load an image with SDL_image or from
     *    raw pixel data, create an SDL_Texture, and return a handle.
     * 3. Here, look up the texture and call SDL_RenderCopy().
     */
    (void)sprite;
    (void)x;
    (void)y;
    printf("[gfx] draw_sprite: not yet implemented.\n");
}

void gfx_cmd_present(void)
{
    SDL_RenderPresent(g_renderer);
}
