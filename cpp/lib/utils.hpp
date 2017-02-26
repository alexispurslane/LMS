#include <vector>
#include "area.hpp"
#include "BearLibTerminal.h"

#pragma once
namespace utils {
    enum class ScreenState { Intro, Game, CharacterSelection, Death };
    enum class SideScreenState { HUD, Skills, Inventory };
    
    template <typename T>
    struct BoundedValue
    {
	T value;
	T max;
	
	bool operator==(T v) { return value == v; }
	
	bool operator<(T v) { return value < v; }
	bool operator>(T v) { return value > v; }
	
	bool operator<=(T v) { return value <= v; }
	bool operator>=(T v) { return value >= v; }
    };

    template<class X, class Y>
    struct GlobalState
    {
	ScreenState screen;
	SideScreenState sidescreen;
	
	std::vector<std::string> messages;
	std::vector<int> scores;
	
	std::unique_ptr<X> map;
	std::unique_ptr<Y> player;
	
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
