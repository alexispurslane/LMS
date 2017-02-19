#include <vector>
#include "../objects/player.hpp"
#include "../terrain_map.hpp"

#pragma once
namespace utils {
    enum ScreenState
    {
	Intro,
	Game,
	CharacterSelection,
	Death
    };

    enum SideScreenState
    {
	HUD,
	Skills,
	Inventory,
	Manual
    };

    struct Point
    {
	int x, y;
    };

    struct GlobalState
    {
	ScreenState screen;
	SideScreenState sidescreen;
	character::Player player;
	std::vector<std::string> messages;
	terrain_map::TerrainMap map;
	int currentselection = 0;
	int turns = 0;
	int message_offset = 0;
	int difficulty = 18;
	//std::vector<int> scores;
	//std::vector<Animation> animations;
    };
}
