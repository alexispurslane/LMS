#include <vector>
#include <variant>
#include "../objects/player.hpp"
#include "../terrain_map.hpp"
#include "../objects/monsters.hpp"
#include "../objects/items.hpp"
#include "BearLibTerminal.h"

#pragma once
namespace utils {
    enum ScreenState { Intro, Game, CharacterSelection, Death };
    enum SideScreenState { HUD, Skills, Inventory };
    enum StaticMapElement { Water,  Fire, GeneralObject, Door };
    enum AreaType { Marble, Dirt, Stone };
    
    typedef std::variant<StaticMapElement, items::Item, monsters::Monster> MapElement;
    
    struct Point
    {
	int x;
	int y;
    };

    struct Area 
    {
	Point start_pos;
	Point end_pos;
	uint width;
	uint height;
    }
    
    template <typename T>
    struct BoundedValue
    {
	T value;
	T max;
    };

    struct Dungeon
    {
	std::vector<monsters::Monster> monsters;
	bool alerted;
	Area areas[];
	MapElement map[][];
	std::set<Point> remembered;
	Point player_start;
	Point down_stairs;
	Point up_stairs;
    };

    struct GlobalState
    {
	ScreenState screen;
	SideScreenState sidescreen;
	character::Player *player;
	std::vector<std::string> messages;
	std::vector<int> scores;
	terrain_map::TerrainMap *map;
	int currentselection = 0;
	int turns = 0;
	int message_offset = 0;
	int difficulty = 18;
    };

    std::string exec(const char* cmd);
    std::string to_upper(std::string str);
    std::vector<color_t> fade_colors(color_t a, color_t b);
    std::vector<std::string> split_string(const std::string& str,
					  const std::string& delimiter);
}
