#include "../lib/utils.hpp"
#include "../lib/area.hpp"
#include <memory>

namespace character
{
    class Player;
};
namespace terrain_map
{
    class TerrainMap;
};

#pragma once
namespace monsters
{
    class Monster;

    using GS = std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap, character::Player>>;

    typedef std::function<void(Monster, character::Player)> Action;

    std::map<std::string, Action> ACTIONS;

    class Monster
    {
    public:
        std::string name;
        std::vector<int> tiles;
        color_t color;
        int speed;
        int health;
        int attack;
        bool aggressive;
        Action action;
        bool ranged;
        void run_ai(GS gs);
    };

    extern std::map<std::string, Monster> MONSTERS;
    void monster_turns(GS gs);
    void load();
}
