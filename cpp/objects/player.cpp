#include "../lib/utils.hpp"
#include "../nouns/races.hpp"
#include "../lib/area.hpp"
#include "../objects/items.hpp"
#include <memory>
#include <random>
#include <functional>
#include <algorithm>
#include <map>
#include <cmath>
#include <set>

using namespace std::placeholders;

typedef std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap, Player> > GS;

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
    inventory = r.starting_inventory;
    std::vector<items::Item> food(8, items::ITEMS[items::FOOD_RATION]);
    std::for_each(food, [](auto x) { x.equip(this); })
    inventory.insert(inventory.end(), food.begin(), food.end());
}

public void character::Player::handle_event(GS gs, char c);
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

public utils::Bounde->value<int> character::Player::skill_with_item(items::Item a)
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
	utils::Bounde->value<int> best_applicable_skill{99999,99999};
	for (auto s : a.categories)
	{
	    if (skill_tree.find(s) == skill_tree.end())
	    {
		skill_tree[s] = {baseline, 0};
	    }
	    if (skill_tree[s] < best_applicable_skill)
	    {
		best_applicable_skill = skill_tree[s];
	    }
	}

	return best_applicable_skill;
    }

    return {8,0};
}

public bool character::Player::can_use(items::Item a)
{
    return skill_with_item(a) <= a.probability && hands >= a.handedness;
}

public bool character::Player::has(items::Item x)
{
    return std::find_if(inventory.begin(), inventory.end(),
			[=](const items::Item i) {
			    return i.equipped && i.tile_code == x.tile_code;
			}) != inventory.end();
}

public int character::Player::score()
{
    return exp*(level->value + kills + defence->value);
}

public void character::Player::learn(GS gs, monsters::Monster m);
{
    exp += floor(m.attack);
    auto s = floor(exp/((75-level->max)+level->value*5));

    if (s >= 1 && s <= level->max && level->value < s)
    {
	level->value = s;
	level_up(gs, s);
    }
}

public void character::Player::level_up(GS gs, int s)
{
    gs->messages->insert("[color=green] You have leveled up!");

    double ratio = health->value / health->max;
    health->max += race.level_up_bonus;
    health->value = health->max * ratio;
    
    strength->value = strength->max += floor(race_level_up_bonus / 10);

    for (auto i : inventory)
    {
	if (i.equipped && (i.broad_category == "Armor" ||
			   i.broad_catagory == "Weapon"))
	{
	    for (auto c : i.categories)
	    {
		skill_tree[c] -= 2;
	    }
	}
    }
}

public void character::Player::rest()
{
    health += 1;
}

public std::tuple<bool, bool> attack_other(GS gs, monsters::Monster &m)
{
    health += min(health->max - health->value, defence);
    auto skill = race.inate_skills.weapon;
    std::mt19937 rng;
    rng.seed(std::random_device()());
    std::uniform_int_distribution<std::mt19937::result_type> chance(0, 20+exp);

    if (m.speed < speed)
    {
	m->attack_other(this, gs);
	if (health->value > 0 && chance(rng) <= exp * skill + 10)
	{
	    m->health -= attack->value;
	    gs->messages->insert(gs->messages->begin(),
				 "[color=yellow]You hit the monster.");
	    gs->messages->insert(gs->messages->begin(),
				 "[color=yellow]The monster's health is " + std::string(m.health));
	}
	else
	{
	    gs->messages->insert(gs->messages->begin(),
				 "[color=red]You miss the monster.");
	}
    }
    else
    {
	m->health -= attack->value;
	if (m.health > 0)
	{
	    m->attack_other(this, gs);
	}
    }

    if (health > 0 && m.health <= 0)
    {
	learn(gs, m);
	kills++;
    }

    return std::make_tuple(health <= 0, m->health <= 0);
}

public bool character::Player::add_inventory_item(items::Item item)
{
    if (inventory.size() < consts::MAX_INVENTORY)
    {
	inventory.push_back(items::Item(item));
	std::vector<int> calculate_weights;
	std::transform(inventory.begin(), inventory.end(),
		       calculate_weights.begin(),
		       std::bind(std::minus<int>(), _1, strength->value));
	speed->value = std::accumulate(calculated_weights);

	if (item.broad_catagory == "Missle")
	{
	    item.equip(this);
	}
	return true;
    }
}
