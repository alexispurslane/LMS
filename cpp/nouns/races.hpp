#include "../lib/utils.hpp"
#include <memory>

#pragma once
namespace races
{
    class Race
    {
	
    };

    const Race WARRIOR{};
    const Race BERSERKER{};
    const Race BOWMAN{};
    const Race RACES[3] = {WARRIOR, BERSERKER, BOWMAN};
}
