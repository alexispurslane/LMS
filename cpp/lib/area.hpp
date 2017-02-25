#include <vector>
#include <cstdlib>
#include <random>

#pragma once
namespace area
{
    enum class AreaType { Marble, Dirt, Stone };
    struct Point
    {
	int x;
	int y;
    };
    
    class Area 
    {
    public:
	Point start_pos;
	Point end_pos;
	int width;
	int height;
	AreaType type;
	
	Area(int x, int y, int w, int h);
	Area(Point maxpos, int minsize, int maxsize);
	
	bool intersects(Point p) const;
	std::vector<Point> edge_points() const;
    };

    /*class Room
    {
    public:
	
    };*/
}
