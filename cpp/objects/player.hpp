#include "../lib/utils.hpp"
#include "../nouns/races.hpp"
#include "../lib/area.hpp"
#include "../terrain_map.hpp"
#include "items.hpp"
#include "monsters.hpp"
#include <memory>
#include <string>
#include <map>
#include <set>
#include <tuple>

#pragma once
namespace character
{
        class Player;
        typedef std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap, Player> > GS;

        class Player
        {
        private:
                area::Point prev_loc;
        public:
                area::Point loc;
                // Housekeeping
                uint light_source_radius = 0;
                uint hands = 2;
                uint poisoned = 0;
                uint frozen = 0;
                int hunger = 0;
                int tile_code = 0xE059;

                // Stats
                std::map<std::string, utils::BoundedValue<uint> > skill_tree{};
                uint kills = 0;
                uint exp = 0;

                // Attributes
                races::Race race;
                utils::BoundedValue<int> health;
                utils::BoundedValue<int> speed;
                utils::BoundedValue<int> level;
                utils::BoundedValue<int> strength;
                utils::BoundedValue<int> attack;
                utils::BoundedValue<int> defence;

                // Inventory
                std::vector<items::Item> inventory;
                std::set<items::Item> dequip_queue;
                items::Item ranged_weapon;
                std::vector<items::Item> missles;

                Player(races::Race r);
                void handle_event(GS gs, char c);
                utils::BoundedValue<int> skill_with_item(items::Item a);
                bool can_use(items::Item a);
                bool has(items::Item x);
                int score();
                void learn(GS gs, monsters::Monster m);
                void level_up(GS gs, int s);
                void rest();
                std::tuple<bool, bool> attack_other(GS gs, monsters::Monster m);
                bool add_inventory_item(items::Item item);
                bool remove_inventory_item(items::Item item);
                int weight();
                bool light();
                bool fast();
                bool noisy();
                std::string attributes();
                void move(GS gs, char d);
        };
}
