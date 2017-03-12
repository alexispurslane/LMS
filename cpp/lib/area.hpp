#include <vector>
#include <cmath>
#include <tuple>
#include <random>

#pragma once
namespace area
{
    enum class AreaType { Marble, Dirt, Stone };
    class Point
    {
    public:
	int x;
	int y;
	Point(int sx, int sy) : x(sx), y(sy) {};
	Point(std::tuple<int, int> t) : x(std::get<0>(t)), y(std::get<1>(t)) {};
	double dist_from_center() const { return sqrt(x*x + y*y); };
	Point operator+(Point o) const { return {x+o.y, y+o.y}; }
	Point operator-(Point o) const { return {x-o.x, y-o.y}; }
	Point operator*(Point o) const { return {x*o.x, y*o.y}; }
	Point operator/(Point o) const { return {x/o.x, y/o.y}; }
	bool operator==(Point o) const { return x == o.x && y == o.y; }
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
}
