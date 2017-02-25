#include "lib/utils.hpp"
#include "objects/items.hpp"
#include "terrain_map.hpp"
#include <memory>

namespace draw 
{
    std::string format_stat(std::string name, items::Item obj);

    typedef std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap, character::Player> > GS;
    
    /* Screen overlay */
    void draw_screen_overlay(GS gs);
    
    void draw_stats(GS gs);
    void draw_messages(GS gs);
    
    void draw_inventory(GS gs);
    void draw_skills(GS gs);

    /* Game screen */
    void draw_screen(GS gs);
    
    void draw_intro_screen(GS gs);
    void draw_charsel_screen(GS gs);
    void draw_death_screen(GS gs);
    void draw_game_screen(GS gs);

    /* Utilities */
    void add_square(GS gs,
		    uint x, uint y,
		    uint width, uint height,
		    std::string text, uint spacing = 2);
}
