#include "BearLibTerminal.h"
#include <algorithm>

#pragma once
namespace draw
{
    int frame = 0;
    /*
     * Game Screen Drawing Functions
     */
    void draw_screen(utils::GlobalState *gs)
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

    void draw_intro_screen(utils::GlobalState *gs)
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
	draw_square(gs, consts.WIDTH/2-7, 21, 14, 20, "TOP 20 SCORES\n"+scores, 1);
    }

    void draw_charsel_screen(utils::GlobalState *gs)
    {
	races::Race selected_race;
	for (int i=0; i < races::RACES.size(); i++)
	{
	    auto race = races::RACES[i];
	    auto color = "black";
	    
	    if (i + 1 == gs.currentselection)
	    {
		selected_race = race;
		color = "red";
	    }

	    terminal_print(consts::WIDTH/2-28, i*2+5,
			   "[bkcolor="+color+"]"+std::to_string(i+1)+") "+race->name);
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
	    draw_square(gs, consts::WIDTH/2-27, 30, 54, 30, std::string(race_display));
	}
    }

    void draw_death_screen(utils::GlobalState *gs)
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
	draw_square(gs, consts::WIDTH/2-27, 30, 54, 30, std::string(endgame_stats));
    }

    void draw_game_screen(utils::GlobalState *gs)
    {
	gs->terrain_map->draw_map(gs);
	for (monsters::Monster m : gs->terrain_map->dungeon->monsters)
	{
	    auto v = gs->terrain_map->dungeon->calculate_fov(gs->player->loc)
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
    void draw_screen_overlay(utils::GlobalState *gs)
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

    void draw_stats(utils::GlobalState *gs)
    {
	auto player = gs->player;
	
	vector<color_t> fade = utils::fade_colors(color_from_name("red"), color_from_argb(1, 25, 25, 25));
	if (frame % fade.size() == 0 && frame / fade.size() % 2 == 0)
	{
	    std::reverse(fade.begin(), fade.end());
	}
	color_t current_color = fade.at(frame % fade.size());
	int bounds = 9;
	int start - consts::MESSAGE_NUMBER+1;
	terminal_color(current_color);
	draw_square(gs, consts::EDGE_POS-1, start, consts::WIDTH-base-2, 11,
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
	auto nm = gs->dungeon->monsters.size();
	terminal_print(base, start+2, "LOS Dist: "+std::to_string(nm));
	terminal_print(base+bounds+4, start+2, 'Dungeon: '+std::to_string(gs->terrain_map->level));

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
}
