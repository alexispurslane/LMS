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
    
    void draw_inventory(utils::GlobalState *gs);
    void draw_skills(utils::GlobalState *gs);

    /* Game screen */
    void draw_screen(utils::GlobalState *gs);
    
    void draw_intro_screen(utils::GlobalState *gs);
    void draw_charsel_screen(utils::GlobalState *gs);
    void draw_death_screen(utils::GlobalState *gs);
    void draw_game_screen(utils::GlobalState *gs);

    /* Utilities */
    void add_square(utils::GlobalState *gs, uint x, uint y, uint width, uint height, std::string text, uint spacing = 2);
}
