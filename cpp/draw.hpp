#include "lib/utils.hpp"
#include "objects/items.hpp"
#include "terrain_map.hpp"

namespace draw 
{
    std::string format_stat(std::string name, items::Item obj);

    /* Screen overlay */
    void draw_screen_overlay(utils::GlobalState *gs);
    void draw_stats(utils::GlobalState *gs);
    void draw_messages(utils::GlobalState *gs);
    void draw_hud_screen(utils::GlobalState *gs);
    void draw_inventory_screen(utils::GlobalState *gs);
    void draw_skills_screen(utils::GlobalState *gs);

    /* Game screen */
    void draw_screen(utils::GlobalState *gs);
    void draw_charsel_screen(utils::GlobalState *gs);
    void draw_intro_screen(utils::GlobalState *gs);
    void draw_death_screen(utils::GlobalState *gs);
    void draw_game_screen(utils::GlobalState *gs);

    /* Tiles */
    void draw_text_tile(utils::GlobalState *gs);
    void draw_text_tile(utils::GlobalState *gs);
    void draw_graphic_tile(utils::GlobalState *gs);

    /* Utilities */
    void add_line(utils::GlobalState *gs);
    void add_square(utils::GlobalState *gs);
}
