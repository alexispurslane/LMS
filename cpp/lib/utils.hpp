#include <vector>
#include "../objects/player.hpp"
#include "../objects/monsters.hpp"
#include "../objects/items.hpp"
#include "area.hpp"
#include "BearLibTerminal.h"

#pragma once
namespace utils {
    enum class ScreenState { Intro, Game, CharacterSelection, Death };
    enum class SideScreenState { HUD, Skills, Inventory };
    enum class StaticMapElement { Floor, Water,  Fire, GeneralObject, OpenDoor, ClosedDoor, Wall };
    enum class AreaType { Marble, Dirt, Stone };
    
    union MapElement
    {
	StaticMapElement sme;
	std::shared_ptr<items::Item> i;
	std::shared_ptr<monsters::Monster> m;
    };
    
    template <typename T>
    struct BoundedValue
    {
	T value;
	T max;
    };

    template<class T>
    struct GlobalState
    {
	ScreenState screen;
	SideScreenState sidescreen;
	std::shared_ptr<character::Player> player;
	std::vector<std::string> messages;
	std::vector<int> scores;
	std::shared_ptr<T> map;
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
