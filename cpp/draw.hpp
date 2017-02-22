#include "lib/utils.hpp"
#include "objects/items.hpp"
#include "terrain_map.hpp"
#include <memory>

namespace draw 
{
    std::string format_stat(std::string name, items::Item obj);

    /* Screen overlay */
    void draw_screen_overlay(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    
    void draw_stats(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    void draw_messages(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    
    void draw_inventory(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    void draw_skills(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);

    /* Game screen */
    void draw_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    
    void draw_intro_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    void draw_charsel_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    void draw_death_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);
    void draw_game_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs);

    /* Utilities */
    void add_square(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs, uint x, uint y, uint width, uint height, std::string text, uint spacing = 2);
}
