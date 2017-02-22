#include "BearLibTerminal.h"

namespace terrain_map
{
    class TerrainMap
    {
    private:
	Dungeon dungeons[];
	uint width;
	uint height;
	
    public:
	Dungeon dungeon;
	uint level;
    }
}
