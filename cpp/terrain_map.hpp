#include "lib/utils.hpp"

namespace terrain_map
{
    class TerrainMap
    {
    private:
	Dungeon *dungeons[];
	uint width;
	uint height;

	void reset_dungeon();
	bool restore_dungeon(int n);
	void place_door(Point p);
	
    public:
	Dungeon *dungeon;
	uint level;
	
	TerrainMap() = default;
	TerrainMap(uint w, uint h) : width(w), height(h) {}

	void draw_map(utils::GlobalState *gs, uint frame);
	void calculate_fov(utils::Point p);
	MapElement element_at(Point p);
	bool on_map(Point x, bool bordered);
	utils::AreaType area_at(Point p);
	bool walkable(Point p);
	void generate_dungeon_map();
	utils::Area[] generate_areas();
	void generate_new_map();
	void put_cell(Point p, bool solid);
    }
}
