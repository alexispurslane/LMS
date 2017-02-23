#include "../lib/utils.hpp"
#include "../lib/area.hpp"
#include "../objects/player.hpp"
#include <memory>
#include <set>

#pragma once
namespace dungeons
{
    enum class StaticMapElement
    {
	Floor,
	Water,
	Fire,
	GeneralObject,
	OpenDoor,
	ClosedDoor,
	Wall
    };
    
    struct MapElement
    {
	StaticMapElement sme;
	std::shared_ptr<items::Item> i;
	std::shared_ptr<monsters::Monster> m;
    };
    struct Dungeon
    {
	std::vector<monsters::Monster> monsters{};
	bool alerted = false;
	std::vector<area::Area> areas{};
	std::vector<std::vector<MapElement> > map{};
	std::set<area::Point> remembered{};
	area::Point player_start{-1, -1};
	area::Point down_stairs{-1, -1};
	area::Point up_stairs{-1, -1};
    };

    template <class T>
    Dungeon generate_new(std::unique_ptr<T>);
    template <class T>
    Dungeon generate_bsp(std::unique_ptr<T>);
    template <class T>
    Dungeon generate_walker(std::unique_ptr<T>);
    Dungeon empty_dungeon();
}
