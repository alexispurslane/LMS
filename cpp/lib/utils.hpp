#include <vector>
#include <cmath>
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
	
	bool operator==(T v) const { return value == v; }
	bool operator<(T v)  const { return value < v;  }
	bool operator>(T v)  const { return value > v;  }
	bool operator<=(T v) const { return value <= v; }
	bool operator>=(T v) const { return value >= v; }
	
	BoundedValue<T> & operator+=(T v) const
	{
	    value = min(max, value + v);
	    return *this;
	}
	
	BoundedValue<T> & operator-=(T v) const
	{
	    value = max(0, value - v);
	    return *this;
	}

	operator std::string() const
	{
	    return std::string(value)+"/"+std::string(max);
	}
    };

    template<class X, class Y>
    struct GlobalState
    {
	ScreenState screen;
	SideScreenState sidescreen;
	
	std::vector<std::string> messages;
	std::vector<int> scores;
	
	X map;
	Y player;
	
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
    template <class T>
    std::string join_string(const std::vector<T> v);
}
