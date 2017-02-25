#include "../lib/utils.hpp"
#include "../nouns/races.hpp"
#include "../lib/area.hpp"
#include "../objects/items.hpp"
#include <memory>
#include <map>
#include <set>

#pragma once
namespace character
{
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

	// Stats
	std::map<std::string, utils::BoundedValue<uint> > skill_tree{};
	uint killed_monsters = 0;
	uint level = 0;
	uint exp = 0;

	// Attributes
	races::Race race;
	utils::BoundedValue<int> health;
	utils::BoundedValue<int> speed;
	utils::BoundedValue<int> strength;
	utils::BoundedValue<int> attack;
	utils::BoundedValue<int> defence;

	// Inventory
	std::vector<items::Item> inventory;
	std::set<items::Item> dequip_queue;
	items::RangedWeapon ranged_weapon;
	std::vector<items::Missle> missles;

	Player(races::Race r);
    };
}
