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
character::Player::Player(races::Race r) : race(r), inventory(r.starting_inventory)
{
    // Starting Stats
    health = r.health;
    speed = r.speed;
    strength = r.strength;
    attack = r.attack;
    defence = r.defence;
    level = r.level;

    // Inventory
    std::vector<items::Item> food(8, items::Item(items::ITEMS["FOOD_RATION"]));
    for (auto x : food)
    {
        food.equip(this);
    }
    inventory.insert(inventory.end(), food.begin(), food.end());
}

int character::Player::handle_event(GS gs, char c);
{
    int time = 0;
    // Dequip used lights
    for (auto i : dequip_queue)
    {
        i.lasts--;
        if (i.lasts <= 0)
        {
            i.dequip(this);
            time++;
            gs->messages.push_back("[color=yellow]Your "+i.name+" flickers out.");
            dequip_queue.erase(std::find(dequip_queue.begin(),
                                         dequip_queue.end(), item));
        }
    }

    // Scheduler
    if (gs->turns % 2 == 0)
    {
        if (poisoned > 0)
        {
            poisoned--;
            time++;
            health.value--;
        }
        if (frozen > 0)
        {
            frozen--;
        }
    }
    else if (gs->turns % 3 == 0)
    {
        if (health.value < health.max)
        {
            health.value++;
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

    if (std::find(consts::PLAYER_MOVEMENT.begin(),
                  consts::PLAYER_MOVEMENT.end(),
                  d) != consts::PLAYER_MOVEMENT.end())
    {
        move(gs, c);
        time += 5;
    }
    else
    {
        switch (c)
        {
        case ';': // Autorest
            for (int i=0; i < std::floor(health->max/2); i++)
            {
                rest();
            }
            break;
        case '<': // Go downstairs
            time += 7;
            if (gs->map[loc] == dungeons::StaticMapElement::DownStairs)
            {
                gs->map.generate_new_map();
                loc = gs->map->dungeon->player_start;
            }
            break;
        case '>': // Go upstairs
            time += 8;
            if (gs->map[loc] == dungeons::StaticMapElement::UpStairs)
            {
                gs->map.restore_dungeon(gs->map.level-1);
                loc = gs->map->dungeon->player_start;
            }
            break;
        case ',':
            time += 5;
            if (!gs->map[loc].i.empty())
            {
                inventory.push_back(gs->map[loc].i.back());
                gs->map[loc].i.pop_back();
            }
        case '.': // Rest
            time += 9;
            rest();
            break;
        }
    }
    return time;
}

utils::BoundedValue<int> character::Player::skill_with_item(items::Item a)
{
    std::string type{a.broad_category};
    int baseline = 0;

    switch (type)
    {
    case "weapon":
    case "ranged_weapon":
        baseline = 15;
    break;
    case "armor":
        baseline = 20;
        break;
    default:
        baseline = 0;
        break;
    }
    if (type == "weapon" || type == "ranged_weapon" || type == "armor")
    {
        utils::BoundedValue<int> best_applicable_skill{99999,99999};
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

bool character::Player::can_use(items::Item a)
{
    return skill_with_item(a) <= a.probability && hands >= a.handedness;
}

bool character::Player::has(items::Item x)
{
    return std::find_if(inventory.begin(), inventory.end(),
                        [=](const items::Item i) {
                            return i.equipped && i.tile_code == x.tile_code;
                        }) != inventory.end();
}

int character::Player::score()
{
    return exp*(level.value + kills + defence.value);
}

void character::Player::learn(GS gs, monsters::Monster m);
{
    exp += floor(m.attack);
    auto s = floor(exp/((75-level.max)+level.value*5));

    if (s >= 1 && s <= level.max && level.value < s)
    {
        level.value = s;
        level_up(gs, s);
    }
}

void character::Player::level_up(GS gs, int s)
{
    gs->messages->insert("[color=green] You have leveled up!");

    double ratio = health.value / health.max;
    health.max += race.level_up_bonus;
    health.value = health.max * ratio;

    strength.value = strength.max += floor(race_level_up_bonus / 10);

    for (auto i : inventory)
    {
        if (i.equipped && (i.broad_category == "armor" ||
                           i.broad_category == "weapon"))
        {
            for (auto c : i.categories)
            {
                skill_tree[c] -= 2;
            }
        }
    }
}

void character::Player::rest()
{
    health += 1;
}

std::tuple<bool, bool> attack_other(GS gs, monsters::Monster &m)
{
    health += min(health.max - health.value, defence);
    auto skill = race.inate_skills.weapon;
    std::mt19937 rng;
    rng.seed(std::random_device()());
    std::uniform_int_distribution<std::mt19937::result_type> chance(0, 20+exp);

    if (m.speed < speed)
    {
        m->attack_other(this, gs);
        if (health.value > 0 && chance(rng) <= exp * skill + 10)
        {
            m->health -= attack.value;
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
        m->health -= attack.value;
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

bool character::Player::add_inventory_item(items::Item item)
{
    if (inventory.size() < consts::MAX_INVENTORY)
    {
        inventory.push_back(items::Item(item));
        speed.value = weight();

        if (item.broad_category == "missle")
        {
            item.equip(this);
        }
        return true;
    }
}

bool character::Player::remove_inventory_item(items::Item item)
{
    if (std::find(inventory.begin(), inventory.end(), item) != inventory.end())
    {
        item.dequip(this);
        inventory.erase(std::find(inventory.begin(),
                                  inventory.end(), item));
        return true;
    }
    return false;
}

int character::Player::weight()
{
    std::vector<int> calculate_weights;
    std::transform(inventory.begin(), inventory.end(),
                   calculate_weights.begin(),
                   [strength](const auto x) { return x.weight-strength; });
    return std::accumulate(calculated_weights);
}

bool character::Player::light()
{
    return weight() < 4;
}

bool character::Player::fast()
{
    return speed < 5;
}

bool character::Player::noisy()
{
    auto armor_count = std::count_if(inventory.begin(), inventory.end(),
                                     [](const auto i) { return i.broad_category == "armor"; });
    auto weapon_count = std::count_if(inventory.begin(), inventory.end(),
                                      [](const auto i) { return i.broad_category == "weapon"; });

    if (race.name == "Bowman")
    {
        return armor_count <= 4 && weapon_count <= 3;
    }
    else
    {
        return armor_count <= 3 && weapon_count <= 3;
    }
}

std::string character::Player::attributes()
{
    std::vector<std::string> attributes;
    if (noisy)
    {
        attributes.push_back("noisy");
    }
    if (light)
    {
        attributes.push_back("light");
    }
    if (fast)
    {
        attributes.push_back("fast");
    }
    return utils::join_string(attributes);
}

void character::Player::move(GS gs, char direction)
{
    if (frozen <= 0)
    {
        std::tuple<int, int> delta;
        switch (direction)
        {
        case 'j':
            delta = consts::SOUTH;
            break;
        case 'k':
            delta = consts::NORTH;
            break;
        case 'h':
            delta = consts::WEST;
            break;
        case 'l':
            delta = consts::EAST;
            break;
        case 'u':
            delta = consts::NORTH_WEST;
            break;
        case 'b':
            delta = consts::SOUTH_WEST;
            break;
        case 'i':
            delta = consts::NORTH_EAST;
            break;
        case 'm':
            delta = consts::SOUTH_EAST;
            break;
        default:
            delta = {0, 0};
        }

        auto npos = loc + area::Point(delta);

        if (loc != npos)
        {
            if (gs->map->walkable(npos) && map >= npos)
            {
                bool cancel = false;
                auto me = gs->map[npos];
                switch (me.sme)
                {
                case dungeons::StaticMapElement::GeneralObject:
                    if (!me.m.empty())
                    {
                        std::tie(player_dead, monster_dead) = attack_other(me.m.back());
                        gs->messages.insert(gs->messages.begin(), "[color=green]You attack the " + me.m.name);

                        if (!monster_dead)
                        {
                            gs->messages.insert(gs->messages.begin(), "[color=red]The "+me.m.name+" attacks you.");
                            gs->messages.insert(gs->messages.begin(), "[color=red]Its health is now "+std::string(me.m.health.value));
                        }
                        else
                        {
                            gs->messages.insert(gs->messages.begin(), "[color=green]You vanquish the "+me.m.name);
                            me.m.drop_reward();
                        }
                    }
                    if (!me.i.empty())
                    {
                        for (auto i : me.i)
                        {
                            if (i.broad_category == "light" ||
                                i.broad_category == "food"  ||
                                i.broad_category == "missle")
                            {
                                if (add_inventory_item(i))
                                {
                                    me.i.erase(std::find(me.i.begin(), me.i.end(), i));
                                    gs->messages.insert(gs->messages.begin(), "You pick up a " + i.name + ".");
                                }
                                else
                                {
                                    gs->messages.insert(gs->messages.begin(), "Your inventory is full.");
                                }
                            }
                            else
                            {
                                gs->messages.insert(gs->messages.begin(), "You find a " + i.name + ".");
                            }
                        }
                    }
                    cancel = true;
                    break;
                case dungeons::StaticMapElement::Wall:
                    cancel = gs->map.area_at(npos).type == area::AreaType::Dirt;
                    if (!cancel)
                    {
                        me.sme = dungeons::StaticMapElement::Floor;
                    }
                    break;
                case dungeons::StaticMapElement::ClosedDoor:
                    me = dungeons::StaticMapElement::OpenDoor;
                    cancel = true;
                    break;
                }

                if (!cancel)
                {
                    loc = npos;
                    gs->map.calculate_fov(npos);
                }
            }
        }
    }
    else
    {
        gs->messages.insert(gs->messages.begin(), "You're frozen.");
    }
}
