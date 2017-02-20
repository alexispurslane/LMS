#include <vector>
#include "../objects/player.hpp"
#include "../terrain_map.hpp"
#include "BearLibTerminal.h"

#pragma once
namespace utils {
    enum ScreenState { Intro, Game, CharacterSelection, Death };
    enum SideScreenState { HUD, Skills, Inventory };
    struct Point { int x, y; };

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

    template<typename Out>
    std::string exec(const char* cmd);
    void split(const std::string &s, char delim, Out result);
    std::vector<std::string> split(const std::string &s, char delim);
    std::string to_upper(std::string str);
    std::vector<color_t> fade_colors(color_t a, color_t b);
}
