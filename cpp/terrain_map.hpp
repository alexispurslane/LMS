#include "lib/utils.hpp"
#include "lib/area.hpp"
#include <memory>
#include <vector>
#include <set>

#pragma once
namespace terrain_map
{
    struct Dungeon
    {
	std::vector<monsters::Monster> monsters;
	bool alerted;
	area::Area areas[6];
	std::vector<std::vector<utils::MapElement> > map;
	std::set<area::Point> remembered;
	area::Point player_start;
	area::Point down_stairs;
	area::Point up_stairs;
    };
    
    class TerrainMap
    {
    private:
	std::vector<std::unique_ptr<Dungeon> > dungeons;
	uint width;
	uint height;

	void reset_dungeon();
	bool restore_dungeon(int n);
	
    public:
	std::unique_ptr<Dungeon> dungeon;
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
	utils::MapElement element_at(area::Point p) const;
	bool on_map(area::Point x, bool bordered) const;
	utils::AreaType area_at(area::Point p) const;
	bool walkable(area::Point p) const;
	std::vector<area::Area> generate_areas() const;
    };
}
