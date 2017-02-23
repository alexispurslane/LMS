#include "../lib/utils.hpp"
#include "../lib/area.hpp"
#include <memory>

#pragma once
namespace dungeons
{
    template <class T>
    Dungeon generate_new(std::unique_ptr<T>) {}
 
    template <class T>
    Dungeon generate_bsp(std::unique_ptr<T>) {}
    
    template <class T>
    Dungeon generate_walker(std::unique_ptr<T>) {}
    
    Dungeon empty_dungeon()
    {
	return new Dungeon;
    }
}
