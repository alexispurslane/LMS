#include <vector>
#include <cstdlib>

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
	
	Area(int x, int y, int w, int h) : width(w), height(h)
	{
	    start_pos = {x,y};
	    end_pos = {x+w, y+h};
	}
	
	inline bool intersects(Point p) const
	{
	    return p.x >= start_pos.x && p.y >= start_pos.y &&
		p.x <= end_pos.x && p.y <= end_pos.y;
	}

	std::vector<Point> edge_points() const;
    };

    /*class Room
    {
    public:
	
    };*/
}
