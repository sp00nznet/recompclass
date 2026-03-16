#include <stdio.h>
#include <SDL2/SDL.h>
#include "graphics_bridge.h"

/*
 * main.c -- Demo program for the graphics bridge.
 *
 * Draws a simple scene with colored rectangles using the abstract
 * graphics command interface.  Press Escape or close the window to exit.
 */

/* Helper to create a GfxColor. */
static GfxColor make_color(uint8_t r, uint8_t g, uint8_t b, uint8_t a)
{
    GfxColor c = { r, g, b, a };
    return c;
}

/* Helper to create a GfxRect. */
static GfxRect make_rect(int x, int y, int w, int h)
{
    GfxRect r = { x, y, w, h };
    return r;
}

int main(int argc, char *argv[])
{
    (void)argc;
    (void)argv;

    /* Initialize the graphics bridge with an 800x600 window. */
    if (gfx_init("Lab 15 - Graphics Bridge Demo", 800, 600) != 0) {
        fprintf(stderr, "Failed to initialize graphics.\n");
        return 1;
    }

    printf("Running demo. Press Escape or close the window to exit.\n");

    int running = 1;
    int frame   = 0;

    while (running) {
        /* Poll SDL events for quit/escape. */
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = 0;
            }
            if (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE) {
                running = 0;
            }
        }

        /* --- Build the frame using abstract commands --- */

        /* Clear to dark blue. */
        gfx_cmd_clear(make_color(20, 20, 60, 255));

        /* Draw a "ground" rectangle. */
        gfx_cmd_draw_rect(make_rect(0, 500, 800, 100), make_color(34, 139, 34, 255));

        /* Draw a "sky" element -- a yellow sun that moves. */
        int sun_x = 100 + (frame % 600);
        gfx_cmd_draw_rect(make_rect(sun_x, 50, 60, 60), make_color(255, 255, 0, 255));

        /* Draw some "buildings". */
        gfx_cmd_draw_rect(make_rect(100, 350, 80, 150), make_color(180, 180, 180, 255));
        gfx_cmd_draw_rect(make_rect(220, 300, 100, 200), make_color(160, 160, 160, 255));
        gfx_cmd_draw_rect(make_rect(370, 380, 70, 120), make_color(200, 200, 200, 255));
        gfx_cmd_draw_rect(make_rect(500, 280, 120, 220), make_color(140, 140, 140, 255));

        /* Draw "windows" on the tallest building. */
        for (int row = 0; row < 4; row++) {
            for (int col = 0; col < 2; col++) {
                gfx_cmd_draw_rect(
                    make_rect(230 + col * 45, 310 + row * 45, 30, 30),
                    make_color(255, 255, 200, 255)
                );
            }
        }

        /* Present the frame. */
        gfx_cmd_present();

        frame++;
    }

    gfx_shutdown();
    return 0;
}
