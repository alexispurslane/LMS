#include "../lib/utils.hpp"
#include "../nouns/races.hpp"
#include "../lib/area.hpp"
#include "../objects/items.hpp"
#include <memory>
#include <algorithm>
#include <map>
#include <set>

public character::Player::Player(races::Race r)
{
    race = r;

    // Starting Stats
    health = r.health;
    speed = r.speed;
    strength = r.strength;
    attack = r.attack;
    defence = r.defence;
    level = r.level;

    // Inventory
    inventory.insert(inventory.end(),
		     r.starting_inventory.begin(),
		     r.starting_inventory.end());
    for (int i=0; i < 4; i++)
    {
	inventory.push_back(items::Item(items::ITEMS[items::FOOD_RATION]));
    }

    // Equip Inventory to Start
    for (auto i : inventory)
    {
	if (!i.id == items::FOOD_RATION)
	{
	    i.equip(this);
	}
    }
}

public void character::Player::handle_event(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap, Player> > gs, char c);
{
    // Dequip used lights
    for (auto i : dequip_queue)
    {
	i.lasts--;
	if (i.lasts <= 0)
	{
	    i.dequip(this);
	    gs->messages.push_back("[color=yellow]Your "+i.name+" flickers out.");
	    dequip_queue.erase(std::remove(dequip_queue.begin(),
					   dequip_queue.end(), i),
			       dequip_queue.end());
	}
    }

    // Sechduler
    if (gs->turns % 2 == 0)
    {
	if (poisoned > 0)
	{
	    poisoned--;
	    health->value--;
	}
    }
    else if (gs->turns % 3 == 0)
    {
	if (health->value < health->max)
	{
	    health->value++;
	}
	if (hunger > 20)
	{
	    auto desc = "hungry";
	    if (hunger > 60)
	    {
		desc = "starving";
	    }
	    else if (hunger > 40)
	    {
		desc = "ravinous";
	    }
	    gs->messages.push_back("[color=red]You feel "+desc);
	}
    }
    else if (gs->turns % 4 == 0)
    {
	hunger += 1;
    }

    move(gs, c);
}

public utils::BoundedValue<int> character::Player::skill_with_item(items::Item a)
{
    std::string type{a.broad_catagory};
    int baseline = 0;

    switch (type)
    {
    case "Weapon":
    case "RangedWeapon":
	baseline = 15;
    break;
    case "Armor":
	baseline = 20;
	break;
    default:
	baseline = 0;
	break;
    }
    if (type == "Weapon" || type == "RangedWeapon" || type == "Armor")
    {
	utils::BoundedValue<int> best_applicable_skill{99999,99999};
	for (auto s : a.categories)
	{
	    if (skill_tree.find(s) == skill_tree.end())
	    {
		skill_tree[s] = baseline;
	    }
	    if (skill_tree[s] < best_applicable_skill)
	    {
		best_applicable_skill = skill_tree[s];
	    }
	}

	return best_applicable_skill;
    }

    return {8,8};
}

public bool character::Player::can_use(items::Item a)
{

}
