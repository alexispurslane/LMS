#include "../lib/utils.hpp"
#include "../objects/items.hpp"
#include <memory>
#include <string>
#include <vector>

#pragma once
namespace races
{
    class Race
    {
    public:
        int suggested_difficulty;
        std::string name;
        int bonus;
        int speed;
        int levels;
        int color;
        std::string description;
        int max_health;
        int strength;
        std::vector<items::Item> starting_inventory;
    };

    const Race WARRIOR{};
    const Race BERSERKER{};
    const Race BOWMAN{};
    const Race RACES[3] = {WARRIOR, BERSERKER, BOWMAN};
}
