#include "lib/utils.hpp"
#include "objects/monsters.hpp"
#include "lib/area.hpp"
#include <memory>
#include <cmath>
#include <vector>

#pragma once
namespace terrain_map
{
    class TerrainMap
    {
    private:
	std::vector<std::unique_ptr<dungeons::Dungeon> > dungeons;
	uint width;
	uint height;
	
	bool restore_dungeon(int n)
	{
	    dungeon = dungeons[n];
	}
	
    public:
	std::unique_ptr<dungeons::Dungeon> dungeon;
	uint level;
	std::set<area::Point> fov;
	
	TerrainMap() = default;
	TerrainMap(uint w, uint h) : width(w), height(h)
	{
	    dungeons::reset_dungeon();
	    this.calculate_fov();
	    this.generate_new_map();
	}

	// Mutating Functions
	// Raycasting Algorithm
	void calculate_fov(area::Point p, int rad)
	{
	    for (int deg=0; deg <= 360; deg++)
	    {
		area::Point outer{p.x + rad*cos(deg), p.y + rad*sin(deg)};
		std::vector<area::Point> line = utils::bresenham(p, outer);
		for (auto p : line)
		{
		    if (element_at(p) == ClosedDoor || element_at(p) == Wall)
		    {
			break;
		    }
		    else
		    {
			fov.insert(p);
		    }
		}
	    }
	}
	
	void generate_new_map()
	{
	    
	    dungeon = std::make_shared<dungeons::Dungeon>(dungeons::generate_new());
	    dungeons.push_back(dungeon);
	}
	
	void put_cell(area::Point p, bool solid)
	{

	}

	// Constant Functions
	void draw_map(std::shared_ptr<utils::GlobalState> gs, uint frame) const
	{

	}

	dungeons::MapElement element_at(area::Point p) const
	{

	}
	
	bool on_map(area::Point p, bool bordered) const
	{
	    if (bordered)
	    {
		return p.x > 0 && p.y > 0 && p.x < width && p.y < height;
	    }
	    else
	    {
		return p.x >= 0 && p.y >= 0 && p.x <= width && p.y <= height;
	    }
	}
	
	area::AreaType area_at(area::Point p) const
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
