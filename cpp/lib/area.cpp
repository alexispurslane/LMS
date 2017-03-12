#include "area.hpp"
#include <vector>
#include <cstdlib>
#include <random>

area::Area::Area(int x, int y, int w, int h) : width(w), height(h)
{
    start_pos = {x,y};
    end_pos = {x+w, y+h};
}

area::Area::Area(Point maxpos, int minsize, int maxsize)
{
    std::random_device rd;
    std::mt19937 gen(rd());
	    
    std::uniform_int_distribution<> posx(0, maxpos.x);
    std::uniform_int_distribution<> posy(0, maxpos.y);
	    
    std::uniform_int_distribution<> sz(minsize, maxsize);
	    
    start_pos = {posx(gen), posy(gen)};
    width = sz(gen);
    height = sz(gen);
    end_pos = {start_pos.x+width, start_pos.y+height};
}
	
bool area::Area::intersects(Point p) const
{
    return p.x >= start_pos.x && p.y >= start_pos.y &&
	p.x <= end_pos.x && p.y <= end_pos.y;
}

std::vector<area::Point> area::Area::edge_points() const
{

}
