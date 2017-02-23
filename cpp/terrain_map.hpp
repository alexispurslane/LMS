#include "lib/utils.hpp"
#include "generators/dungeons.hpp"
#include "lib/area.hpp"
#include <memory>
#include <vector>
#include <set>

#pragma once
namespace terrain_map
{    
    class TerrainMap
    {
    private:
	std::vector<std::unique_ptr<dungeons::Dungeon> > dungeons;
	uint width;
	uint height;

	void reset_dungeon();
	bool restore_dungeon(int n);
	
    public:
	std::unique_ptr<dungeons::Dungeon> dungeon;
	uint level;
	std::set<area::Point> fov;
	
	TerrainMap() = default;
	TerrainMap(uint w, uint h) : width(w), height(h) {}

	// Mutating Functions
	void calculate_fov(area::Point p);
	void generate_dungeon_map();
	void generate_new_map();
	void put_cell(area::Point p, bool solid);

	// Constant Functions
	void draw_map(std::shared_ptr<utils::GlobalState<TerrainMap>> gs, uint frame) const;
	dungeons::MapElement element_at(area::Point p) const;
	bool on_map(area::Point x, bool bordered) const;
	area::AreaType area_at(area::Point p) const;
	bool walkable(area::Point p) const;
	std::vector<area::Area> generate_areas() const;
    };
}
