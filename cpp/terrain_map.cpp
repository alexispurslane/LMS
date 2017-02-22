#include "lib/utils.hpp"
#include "objects/monsters.hpp"
#include "lib/area.hpp"
#include <memory>
#include <vector>

#pragma once
namespace terrain_map
{
    class TerrainMap
    {
    private:
	std::unique_ptr<Dungeon> dungeons[];
	uint width;
	uint height;

	void reset_dungeon()
	{
	    dungeon->alerted = false;
	    dungeon->monsters = std::vector<monsters::Monster>();
	    dungeon->areas = new area::Areas[] {};
	    dungeon->map = new utils::MapElment[][] {};
	    dungeon->remembered = std::set<area::Point>();
	    dungeon->player_start = {30, 30};
	    dungeon->down_stairs = {1, 1};
	    dungeon->up_stairs = {31, 31};
	    
	}
	bool restore_dungeon(int n)
	{
	    dungeon = dungeons[n];
	}
	
    public:
	std::unique_ptr<Dungeon> dungeon;
	uint level;
	std::set<area::Point> fov;
	
	TerrainMap() = default;
	TerrainMap(uint w, uint h) : width(w), height(h)
	{
	    this.reset_dungeon();
	    this.calculate_fov();
	    this.generate_new_map();
	}

	// Mutating Functions
	void calculate_fov(area::Point p)
	{

	}
	void generate_dungeon_map()
	{

	}
	void generate_new_map()
	{

	}
	void put_cell(area::Point p, bool solid)
	{

	}

	// Constant Functions
	void draw_map(std::shared_ptr<utils::GlobalState> gs, uint frame) const
	{

	}
	utils::MapElement element_at(area::Point p) const
	{

	}
	bool on_map(area::Point x, bool bordered) const
	{

	}
	utils::AreaType area_at(area::Point p) const
	{
	    for (Area a : dungeon->areas)
	    {

	    }
	}
	bool walkable(area::Point p) const
	{
	    return dungeon->map[p.y][p.x] != utils::ClosedDoor &&
		dungeon->map[p.y][p.x] != utils::Wall;
	}
	area::Area[] generate_areas() const;
    };
}

// Run calculate_fov(*gs->player->loc) every player move
