#include "lib/utils.hpp"
#include "BearLibTerminal.h"
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
		    if (this[p] == ClosedDoor || this[p] == Wall)
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
	    level++;
	}
	
	void put_cell(area::Point p, dungeons::MapElement el)
	{
	    dungeon->map[p.y][p.x] = std::make_shared<dungeons::MapElement>(el);
	}

	// Constant Functions
	void draw_map(GS gs, uint frame) const
	{
	    for (int y=0; y < consts::HEIGHT; y++)
	    {
		for (int x=0; x < consts::WIDTH; x++)
		{
		    if (std::find(fov.begin(), fov.end(), area::Point(x, y)) != v.end())
		    {
			char x = 0xE000;
			auto c = color_from_name("white");
			auto t = dungeon->map[y][x];
		    
			switch (t.sme)
			{
			case dungeons::StaticMapElement::Water:
			    x += 5;
			    c = color_from_name("sea");
			    break;
			case dungeons::StaticMapElement::Fire:
			    x += 5;
			    c = color_from_name("flame");
			    break;
			case dungeons::StaticMapElement::OpenDoor:
			    c = color_from_name("#966F33");
			    break;
			case dungeons::StaticMapElement::ClosedDoor:
			    x += 14;
			    c = color_from_name("#966F33");
			    break;
			case dungeons::StaticMapElement::Wall:
			    auto a = area_at({x,y}, false);
			    switch (a.type)
			    {
			    case Marble:
				x += 1;
				c = color_from_name("white");
				break;
			    case Stone:
				x += 2;
				c = color_from_name("darker white");
				break;
			    case Dirt:
				x += 32;
				c = color_from_name("darker #966F33");
				break;
			    }
			    std::set<dungeons::MapElement> adj
			    {
				this[{x-1, y}], this[{x, y-1}], this[{x+1, y}], this[{x, y+1}],
			    };
			    
			    if (std::find_if(adj.begin(), adj.end(),
					     [](dungeons::MapElement x) { return x.sme == t.sme; })
				== adj.end())
			    {
				x = 0xE020;
			    }
			case dungeons::StaticMapElement::UpStairs:
			    x += 13;
			    c = color_from_name("dark white");
			    break;
			case dungeons::StaticMapElement::DownStairs:
			    x += 12;
			    c = color_from_name("darkest white");
			    break;
			case dungeons::StaticMapElement::GeneralObject:
			    if (t.i != nullptr)
			    {
				x += t->i.front->tile_code;
			    }
			    if (t.m != nullptr)
			    {
				x += t->m.front->color_fg;
				x += t->m.front->tile_code;
			    }
			}
		    }
		}
	    }
	}

	dungeons::MapElement operator[](area::Point p) const
	{
	    return dungeon->map[p.y][p.x];
	}

	bool operator>(area::Point p) const
	{
	    return contains(p, true);
	}
	
	bool operator>=(area::Point p) const
	{
	    return contains(p, false);
	}
	
	bool contains(area::Point p, bool bordered) const
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
	
	area::Area area_at(area::Point p) const
	{
	    return std::find_if(dungeon->areas.begin(),
				dungeon->areas.end(),
				[=](area::Area a) { return a.includes(p); });
	}
	
	bool walkable(area::Point p) const
	{
	    return this[p].sme != dungeons::StaticMapElement::ClosedDoor &&
		this[p].sme != dungeons::StaticMapElement::Wall &&
		!(this[p].sme == dungeons::StaticMapElement::GeneralObject &&
		  this[p].m != nullptr);
	}
	area::Area[] generate_areas() const
	{
	    for (int i=0; i < 6; i++)
	    {
		dungeon->areas.push_back(area::Area());
	    }
	}
    };
}

// Run calculate_fov(*gs->player->loc) every player move
