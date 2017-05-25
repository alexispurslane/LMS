#include "lib/utils.hpp"
#include "objects/monsters.hpp"
#include "BearLibTerminal.h"
#include "lib/area.hpp"
#include <memory>
#include <cmath>
#include <vector>

terrain_map::TerrainMap::TerrainMap(uint w, uint h) : width(w), height(h)
{
    dungeons::reset_dungeon();
    this.calculate_fov();
    this.generate_new_map();
}

// Mutating Functions
// Raycasting Algorithm
void terrain_map::TerrainMap::calculate_fov(area::Point p, int rad)
{
    for (int deg=0; deg <= 360; deg++)
    {
        area::Point outer{p.x + rad*cos(deg), p.y + rad*sin(deg)};
        for (auto p : utils::bresenham(p, outer))
        {
            fov.insert(p);
            if (this[p] == ClosedDoor || this[p] == Wall)
            {
                break;
            }
        }
    }
}

bool terrain_map::TerrainMap::restore_dungeon(int n)
{
    dungeon = dungeons[n];
    level = n;
}

bool terrain_map::TerrainMap::generate_new_map()
{
    if (level < consts::DUNGEONS)
    {
        level++;
        if (level < dungeons.size())
        {
            dungeon = dungeons[level];
        }
        else
        {
            dungeon = std::make_shared<dungeons::Dungeon>(dungeons::generate_new());
            dungeons.push_back(dungeon);
        }
        return true;
    }
    return false;
}

void terrain_map::TerrainMap::put_cell(area::Point p, dungeons::MapElement el)
{
    dungeon->map[p.y][p.x] = std::make_shared<dungeons::MapElement>(el);
}

// Constant Functions
template <class T>
void terrain_map::TerrainMap::draw_map(std::shared_ptr<T> gs, uint frame) const
{
    for (int y=0; y < consts::HEIGHT; y++)
    {
        for (int x=0; x < consts::WIDTH; x++)
        {
            if (std::find(fov.begin(), fov.end(), area::Point(x, y)) != v.end())
            {
                std::vector<int> tiles;
                char tile = 0xE000;
                auto c = color_from_name("white");
                auto t = dungeon->map[y][x];

                switch (t.sme)
                {
                case dungeons::StaticMapElement::Water:
                    tile += 5;
                    c = color_from_name("sea");
                    break;
                case dungeons::StaticMapElement::Fire:
                    tile += 5;
                    c = color_from_name("flame");
                    break;
                case dungeons::StaticMapElement::OpenDoor:
                    c = color_from_name("#966F33");
                    break;
                case dungeons::StaticMapElement::ClosedDoor:
                    tile += 14;
                    c = color_from_name("#966F33");
                    break;
                case dungeons::StaticMapElement::Wall:
                    auto a = area_at({x,y}, false);
                    switch (a.type)
                    {
                    case Marble:
                        tile += 1;
                        c = color_from_name("white");
                        break;
                    case Stone:
                        tile += 2;
                        c = color_from_name("darker white");
                        break;
                    case Dirt:
                        tile += 32;
                        c = color_from_name("darker #966F33");
                        break;
                    }
                    std::set<dungeons::MapElement> adj
                    {
                        this[{x-1, y}], this[{x, y-1}], this[{x+1, y}], this[{x, y+1}];
                    };

                    if (std::find_if(adj.begin(), adj.end(),
                                     [](dungeons::MapElement x) { return x.sme == t.sme; })
                        == adj.end())
                    {
                        tile = 0xE01D;
                    }
                case dungeons::StaticMapElement::UpStairs:
                    tile += 13;
                    c = color_from_name("dark white");
                    break;
                case dungeons::StaticMapElement::DownStairs:
                    tile += 12;
                    c = color_from_name("darkest white");
                    break;
                case dungeons::StaticMapElement::GeneralObject:
                    if (t.i != nullptr)
                    {
                        c = t->i.front->color;
                        tile = t->i.front->c;
                    }
                    if (t.m != nullptr)
                    {
                        c = t->i.front->color;
                        tile = t->m.front->tile;
                        tiles = t->m.front->tiles;
                    }
                }

                if (tiles.size() == 4)
                {
                    terminal_put(x, y,     tiles[0]);
                    terminal_put(x+1, y,   tiles[1]);
                    terminal_put(x, y+1,   tiles[2]);
                    terminal_put(x+1, y+1, tiles[3]);
                }
                else
                {
                    terminal_put(x, y, tile);
                }
                terminal_color(c);
                terminal_color(color_from_name("white"));
            }
        }
    }
}

dungeons::MapElement& terrain_map::TerrainMap::operator[](area::Point p) const
{
    return dungeon->map[p.y][p.x];
}

bool terrain_map::TerrainMap::operator>(area::Point p) const
{
    return contains(p, true);
}

bool terrain_map::TerrainMap::operator>=(area::Point p) const
{
    return contains(p, false);
}

bool terrain_map::TerrainMap::contains(area::Point p, bool bordered) const
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

area::Area terrain_map::TerrainMap::area_at(area::Point p) const
{
    return std::find_if(dungeon->areas.begin(),
                        dungeon->areas.end(),
                        [=](area::Area a) { return a.includes(p); });
}

bool terrain_map::TerrainMap::walkable(area::Point p) const
{
    bool simple_monster_check = this[p].m != nullptr;

    bool found_overlapping_monster = false;
    for (auto m : dungeon->monsters)
    {
        Point p1{m.loc.x+1, m.loc.y};
        Point p2{m.loc.x, m.loc.y+1};
        Point p3{m.loc.x+1, m.loc.y+1};
        if (p == p1 || p == p2 || p == p3)
        {
            found_overlapping_monster = true;
        }
    }
    bool complex_monster_check = simple_monster_check && found_overlapping_monster;

    bool basic_walk = this[p].sme != dungeons::StaticMapElement::ClosedDoor &&
        this[p].sme != dungeons::StaticMapElement::Wall && simple_monster_check;

    return basic_walk && !complex_monster_check;
}

area::Area[] terrain_map::TerrainMap::generate_areas() const
{
    for (int i=0; i < 6; i++)
    {
        dungeon->areas.push_back(area::Area());
    }
}
