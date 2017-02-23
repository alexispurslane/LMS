#include "BearLibTerminal.h"
#include "objects/items.hpp"
#include <algorithm>
#include <map>

#pragma once
namespace draw
{
    int frame = 0;
    /*
     * Game Screen Drawing Functions
     */
    void draw_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	frame++;
	terminal_clear();

	switch (gs->screen)
	{
	case utils::Intro:
	    draw_intro_screen(gs);
	    break;
	case utils::Death:
	    draw_death_screen(gs);
	    break;
	case utils::Game:
	    draw_game_screen(gs);
	    draw_screen_overlay(gs);
	    break;
	case utils::CharacterSelection:
	    draw_charsel_screen(gs);
	    break;
	}

	terminal_refresh();
    }

    void draw_intro_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	auto text = utils::exec(("figlet -f gothic -m packed '"+consts::TITLE+"'").c_str());
	auto lines = utils::split(text, "\n");
	for (int i=0; i < lines.size(); i++)
	{
	    terminal_print(consts::WIDTH/2-1, i+1, ("[color=red]"+lines[i]).c_str());
	}
	terminal_print(consts::WIDTH/2-12, 18, "[bkcolor=red]press any key to continue");

	std::string scores = "";
	for (auto score : gs->scores)
	{
	    scores += std::to_string(score)+"\n";
	}
	add_square(gs, consts.WIDTH/2-7, 21, 14, 20, "TOP 20 SCORES\n"+scores, 1);
    }

    void draw_charsel_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	races::Race selected_race;
	for (int i=0; i < races::RACES.size(); i++)
	{
	    auto race = races::RACES[i];
	    
	    if (i + 1 == gs->currentselection)
	    {
		selected_race = race;
		terminal_bkcolor("red");
	    }

	    terminal_print(consts::WIDTH/2-28, i*2+5, std::to_string(i+1)+") "+race->name);
	}

	if (selected_race != nullptr)
	{
	    char *race_display =
		"BASELINE STATS"
		"[color=yellow]Level-Up Bonus: %d"
		"[color=turquoise]Speed: %d"
		"[color=red]Number of Levels: %d"
		"[color=grey]Strength: %d"
		"[color=green]Health: %d"
		"[color=white]Description: %s";
	    char *buffer = new char[strlen(race_display)+12+selected_race.description.size()];
	    sprintf(buffer, race_display,
		    selected_race->level_up_bonus,
		    selected_race->speed,
		    selected_race->levels,
		    selected_race->starting.strength,
		    selected_race->starting.max_health,
		    selected_race->description);
	    add_square(gs, consts::WIDTH/2-27, 30, 54, 30, std::string(buffer));

	    // FIXME: Possible use-after-delete bug.
	    delete[] race_display;
	    delete[] buffer;
	}
    }

    void draw_death_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	auto player = gs->player;

	char *endgame_stats =
	    "GAME STATS"
	    "[color=yellow]Turns: %d"
	    "[color=green]Score: %d"
	    "[color=red]Kills: %d"
	    "[color=turquoise]Exp: %d";
	char *buffer = new char[strlen(endgame_stats)+24];
	sprintf(buffer, endgame_stats,
		gs->turns,
		player->score(gs),
		player->kills,
		player->exp);
	add_square(gs, consts::WIDTH/2-27, 30, 54, 30, std::string(buffer));

	// FIXME: Possible use-after delete bug.
	delete[] endgame_stats;
	delete[] buffer;
    }

    void draw_game_screen(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	gs->map->draw_map(gs, frame);
	for (monsters::Monster m : gs->map->dungeon->monsters)
	{
	    auto v = gs->map->fov;
	    
	    if (std::find(v.begin(), v.end(), m->loc) != v.end())
	    {
		terminal_color(m->color_fg);
		terminal_put(m->loc->x + gs->offset->x,
			     m->loc->y + gs->offset->y,
			     0xE100+m->tile_code);
	    }
	}

	terminal_put(gs->player->loc->x + gs->offset->x,
		     gs->player->loc->y + gs->offset->y,
		     0xE100 + gs->player->tile_code);
    }

    /*
     * Overlay Screen Drawing Functions
     */
    void draw_screen_overlay(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	switch (gs->sidescreen)
	{
	case utils::HUD:
	    draw_stats(gs);
	    draw_messages(gs);
	    break;
	case utils::Skills:
	    draw_skills(gs);
	    break;
	case utils::Inventory:
	    draw_inventory(gs);
	    break;
	}
    }

    void draw_stats(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	auto player = gs->player;	
	int bounds = 9;
	int start - consts::MESSAGE_NUMBER+1;
	add_square(gs, consts::EDGE_POS-1, start, consts::WIDTH-base-2, 11,
		    utils::to_upper(player->race->name+"("+player->attributes()+")"));

	/*
	 * Health
	 */
	terminal_print(base, start+1,
		       "Health: "+std::to_string(player->health->value)+
		       "/"+std::string(player->health->value));
	
	int hp = floor(player->health->value / player->health->max);
	if (hp >= 90)
	{
	    terminal_bkcolor(color_from_name("green"));
	}
	else if (hp >= 40)
	{
	    terminal_bkcolor(color_from_name("yellow"));
	}
	else
	{
	    terminal_bkcolor(color_from_name("red"));
	}

	double ratio = 12 / player->health->max;
	
	std::string bar{floor(ratio * player->health->value), ' '};
	terminal_print(base+bounds-3, start+1, bar);

	if (player->poisoned)
	{
	    terminal_bkcolor("lime");
	}
	else
	{
	    terminal_bkcolor("grey");
	}

	std::string filling{ceil(ratio * (player->health->max - player->health->value))};
	terminal_print(base+bounds-3, start+1, underbar);

	auto str = "Stuffed";
	if (player->hunger >= 60)
	{
	    str = "Starving";
	    terminal_color(color_from_name("pink"));
	}
	else if (player->hunger >= 40)
	{
	    str = "Nearly Starving";
	    terminal_color(color_from_name("red"));
	}
	else if (player->hunger >= 20)
	{
	    str = "Hungry";
	    terminal_color(color_from_name("orange"));
	}
	else if (player->hunger >= 15)
	{
	    str = "Nearly Hungry";
	    terminal_color(color_from_name("yellow"));
	}
	else if (player->hunger <= 0)
	{
	    str = "Full";
	    terminal_color(color_from_name("green"));
	}
	else if (player->hunger <= -20)
	{
	    str = "Stuffed";
	    terminal_color(color_from_name("blue"));
	}
	terminal_print(base + bounds + 13, start + 1, str);
	
	/*
	 * Dungeon Level + LOS Distance
	 */
	auto nm = gs->map->dungeon->monsters.size();
	terminal_print(base, start+2, "LOS Dist: "+std::to_string(nm));
	terminal_print(base+bounds+4, start+2, 'Dungeon: '+std::to_string(gs->map->level));

	/*
	 * Player Level
	 */
	auto lvl = floor(player->level / player->race->levels);
	if (lvl <= 50)
	{
	    terminal_color(color_from_name("orange"));
	}
	else
	{
	    terminal_color(color_from_name("blue"));
	}
	terminal_print(base, start+4, 'LVL: '+std::to_string(player->level)+"/"+std::to_string(player->race->levels));

	/*
	 * Player Stats
	 */
	struct Stat
	{
	    std::string name;
	    int stat;
	    std::string color;
	};
	std::vector<Stat> stats
	{
	    { "Strength", player->strength, "green" },
	    { "Speed",    player->speed,    "blue"  },
	    { "Attack",   player->attack,   "red"   },
	    { "Armor",    player->armor,    "grey"  },
	}
	for (auto stat : stats)
	{
	    terminal_color(color_from_name(stat.color));
	    terminal_print(base, start+i, stat.name+": "+std::to_string(stat.stat));
	}

	/*
	 * Ranged Weapon Info
	 */
	if (player->ranged_weapon != nullptr)
	{
	    terminal_print(base, start+9, "RW: "+player->ranged_weapon->name);
	    terminal_print(base+bounds+4, start+9, "Missle #: "+std::to_string(player->missles->size()));
	}

	/*
	 * Game State
	 */
	terminal_print(base, start+10, "Turn: "+std::to_string(gs->turns));
	terminal_print(base+bounds+4, start+10, "Score: "+std::to_string(player->score(gs)));
    }

    void draw_messages(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	std::vector<std::string> ms;
	if (gs->messages.size() >= consts::MESSAGE_NUMBER)
	{
	    ms = std::vector(gs->messages.end() - consts::MESSAGE_NUMBER,
					gs->messages.end());
	}
	else
	{
	    ms = gs->messages;
	}

	ms.insert("MESSAGES");
	
	std::string message_text = "";
	for (auto message : ms)
	{
	    message_text += message+"\n";
	}
	add_square(gs, consts::EDGE_POS-1, 0, consts::WIDTH-consts::EDGE_POS-2,
		   consts::MESSAGE_NUMBER, message_text, 1);
    }

    void draw_inventory(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	int placing = 1;
	add_square(gs, consts::EDGE_POS, 0, floor(consts::WIDTH/2)-4,
		   consts::HEIGHT-1, "INVENTORY (HANDS FREE: "+std::to_string(gs->player->hands_free)+")");
	for (int i=0; i < player->inventory.size(); i++)
	{
	    items::Item a = player->inventory.at(i);
	    if (a.equipped)
	    {
		color_t color = utils::skill_color(gs->player->skill_with_item(a).value);
		terminal_bkcolor(color);
		terminal_color(color);
	    }
	    else if (gs->currentselection == i)
	    {
		color_t color = color_from_name("red");
		terminal_bkcolor(color);
		terminal_color(color);
	    }
	    if (header_bg_color == color_from_name("white"))
	    {
		teminal_color(color_from_name("grey"));
	    }
	    terminal_print(consts::EDGE_POS+1, placing, std::to_string(i+1)+") "+a.name+"("+a.chr+")");
	    std::string str = a.format();
	    for (auto line : utils::split(str, "\n"))
	    {
		placing++;
		terminal_print(consts::EDGE_POS+5, placing, line);
	    }
	    placing += 2;
	}
    }

    void draw_skills(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs)
    {
	std::string text{""};
	auto skill_tree = gs->player->skill_tree;
	int pos = 1;

	auto iter = skill_tree.begin(); // std::map<std::string, utils::BoundedValue>::iterator
	while(iter != skill_tree.end())
	{
	    std::string skill = iter->first();
	    int progress = iter->second();
	    int bar_base_x = ceil((skill.size()+1) / 2);
	    for (int i = 1; i < progress->max - progress->value; i++)
	    {
		terminal_bkcolor(utils::skill_color(progress->value));
		terminal_put(pos + bar_base_x, consts::HEIGHT-(i+4), '   ');

		add_square(gs, pos, consts::HEIGHT-4, skill.size()+1, 1, "\n"+utils::to_upper(skill), 1);
		pos += skill.size()+2;
	    }
	    
	    iter++;
	}

	add_square(gs, 0, 0, consts::WIDTH-1, consts::HEIGHT-1,
		   "SKILLS (LEARNING "+std::to_tring(skill_tree.size())+")");
    }

    /*
     * Draw Utilities
     */
    void add_square(std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap> > gs, uint x, uint y, uint width, uint height, std::string text, uint spacing = 2)
    {
	// FIXME: Possibly off-kilter
	terminal_clear_area(x, y, width, height);
	vector<color_t> fade = utils::fade_colors(color_from_name("red"), color_from_argb(1, 25, 25, 25), 25);
	if (frame % fade.size() == 0 && frame / fade.size() % 2 == 0)
	{
	    std::reverse(fade.begin(), fade.end());
	}
	color_t current_color = fade.at(frame % fade.size());
	terminal_color(current_color);

	// Top
	for (int i=0; i < width; i++)
	{
	    terminal_put(x+i, y, consts::CHAR_DHLINE);
	}

	// Left
	for (int i=0; i < height; i++)
	{
	    terminal_put(x, y+i, consts::CHAR_DVLINE);
	}

	// Bottom
	for (int i=0; i < width; i++)
	{
	    terminal_put(x+i, y+height-1, consts::CHAR_DHLINE);
	}

	// Right
	for (int i=0; i < height; i++)
	{
	    terminal_put(x+width-1, y+i, consts::CHAR_DVLINE);
	}

	// Corners
	terminal_put(x, y, consts::CHAR_DSE);
	
	terminal_put(x+width-1, y, consts::CHAR_DSW);
	terminal_put(x, y+height-1, consts::CHAR_DNE);
	
	terminal_put(x+width-1, y+height-1, consts::CHAR_DNW);

	for (auto line : text)
	{
	    terminal_print(x+1, y+i*spacing, line);
	}
    }
}