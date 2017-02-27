#include "../lib/utils.hpp"
#include "../lib/area.hpp"
#include <memory>

template <class T>
Dungeon dungeons::generate_new(std::unique_ptr<T>) {}
 
template <class T>
Dungeon dungeons::generate_bsp(std::unique_ptr<T>) {}
    
template <class T>
Dungeon dungeons::generate_walker(std::unique_ptr<T>) {}
    
Dungeon dungeons::empty_dungeon()
{
    return new Dungeon;
}
