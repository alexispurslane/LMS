#include "lib/utils.hpp"
#include "terrain_map.hpp"

namespace draw 
{
    std::string format_stat(std::string name, Item obj);

    /* Screen overlay */
    void draw_screen_overlay(GlobalState *gs);
    void draw_stats(GlobalState *gs);
    void draw_messages(GlobalState *gs);
    void draw_hud_screen(GlobalState *gs);
    void draw_inventory_screen(GlobalState *gs);
    void draw_skills_screen(GlobalState *gs);

    /* Game screen */
    void draw_screen(GlobalState *gs);
    void draw_charsel_screen(GlobalState *gs);
    void draw_intro_screen(GlobalState *gs);
    void draw_death_screen(GlobalState *gs);
    void draw_game_screen(GlobalState *gs);

    /* Tiles */
    void draw_text_tile(GlobalState *gs);
    void draw_text_tile(GlobalState *gs);
    void draw_graphic_tile(GlobalState *gs);

    /* Utilities */
    void add_line(GlobalState *gs);
    void add_square(GlobalState *gs);
}
