#include "BearLibTerminal.h"

#include <vector>
#include <cstdlib>
#include <ctime>
#include <string>
#include <map>
#include <cmath>
#include <random>
#include <fstream>
#include <sstream>

#include "lib/area.hpp"
#include "lib/colors.hpp"
#include "lib/consts.hpp"
#include "lib/utils.hpp"

#include "nouns/races.hpp"

#include "objects/items.hpp"
#include "objects/monsters.hpp"
#include "objects/player.hpp"

#include "terrain_map.hpp"
#include "draw.hpp"

int main()
{
    int mouse_scroll_step = 2;
    
    terminal_open();

    terminal_set(("window.title='"+consts::TITLE+"';").c_str());
    terminal_set(("window.size="+std::to_string(consts::WIDTH)+"x"+std::to_string(consts::HEIGHT)+";").c_str());
    terminal_set("font: assets/font/IBMCGA16x16_gs_ro.png, size=16x16, codepage=437;");
    terminal_set("U+E000: assets/tileset8x8.png, size=8x8, align=top-left;");
    terminal_set("stone font: ../Media/Aesomatica_16x16_437.png, size=16x16, codepage=437, spacing=2x1, transparent=#FF00FF;");
    terminal_set("huge font: assets/font/VeraMono.ttf, size=20x40, spacing=2x2");
    terminal_composition(TK_ON);

    terrain_map::TerrainMap tmap{consts::WIDTH, consts::HEIGHT};
    character::Player player{races::WARRIOR};
    
    utils::GlobalState *gamestate;
    gamestate->screen     = utils::Intro;
    gamestate->sidescreen = utils::HUD;
    gamestate->map        = &tmap;
    gamestate->player     = &player;

    std::ifstream infile(".gamescores");
    std::string line;
    while (std::getline(infile, line))
    {
	std::istringstream iss(line);
        int score = 0;
        if (!(iss >> score)) { break; } // error
	gamestate->scores.push_back(score);
    }

    while (true)
    {
	// Update Screen
	if (player->health <= 0 && gamestate->screen != utils::Death)
	{
	    gamestate->screen = utils::Death;
	}
	draw::draw_screen(gamestate);

	// Handle Events
	terminal_setf("input.filter = [keyboard, arrows, q, mouse]");

	if (terminal_has_input())
	{
	    int event = terminal_read();

	    if (event == TK_CLOSE)
	    {
		break;
	    }
	    else if (event == TK_MOUSE_RIGHT)
	    {
		int mx = terminal_check(TK_MOUSE_X);
		int my = terminal_check(TK_MOUSE_Y);

		int map_x = std::max(0, player->loc.x-floor(consts::WIDTH / 4));
		int map_y = std::max(0, player->loc.y-floor(consts::HEIGHT / 2));
		utils::Point cell{mx+map_x, my+map_y};

		auto m = tmap.get_monster_at(cell);
		auto i = tmap.get_item_at(cell);
		auto d = tmap.get_decor_at(cell);
		auto t = tmap.get_cell_type(cell);

		std::string id = terrain_map::TERRAIN_TO_STRING[t];
		if (m != nullptr)
		{
		    id = "a " + m.name;
		}
		else if (i != nullptr)
		{
		    id = "an " + i.name;
		}
		else if (d != nullptr)
		{
		    id = "some " + d.name;
		}

		gamestate->messages.push_back("You see " + id + " here.");
	    }
	    else if (event == TK_MOUSE_SCROLL)
	    {
		gamestate->message_offset += mouse_scroll_step * terminal_state(TK_MOUSE_WHEEL);
	    }
	    else
	    {
		if (gamestate->sidescreen == utils::Inventory)
		{
		    switch (event)
		    {
		    case TK_UP:
			gamestate->currentselection--;
			gamestate->currentselection %= player->inventory.size();
			break;
		    case TK_DOWN:
			gamestate->currentselection++;
			gamestate->currentselection %= player->inventory.size();
			break;
		    case TK_D:
			auto item = player->inventory[gamestate->currentselection];
			item.count--;

			auto single_item = Item(item);
			single_item.count = 1;
		    
			tmap.dungeon.items[player->loc.y][player->loc.x].push_back(single_item);
			break;
		    case TK_RETURN:
			player->inventory[gamestate->currentselection].equip(player);
			break;
		    case TK_ESCAPE:
			player->inventory[gamestate->currentselection].dequip(player);
			break;
		    case TK_I:
			gamestate->sidescreen = utils::HUD;
			break;
		    default:
			break;
		    }
		}
		else if (gamestate->screen == utils::Intro)
		{
		    gamestate->screen = utils::CharacterSelection;
		}
		else if (gamestate->screen == utils::CharacterSelection)
		{
		    switch (event)
		    {
		    case TK_UP:
			gamestate->currentselection--;
			gamestate->currentselection %= races::RACES.size();
			break;
		    case TK_DOWN:
			gamestate->currentselection++;
			gamestate->currentselection %= races::RACES.size();
			break;
		    case TK_RETURN:
			auto racen = gamestate->currentselection-1;
			auto race = races::RACES[racen];
			gamestate->player = character::Player(race);
			gamestate->difficulty = race.suggested_difficulty;
			player->loc = tmap.generate_new_map();
			gamestate->screen = utils::Game;
			break;
		    }
		}
		else if (gamestate->screen == utils::Game)
		{
		    player->handle_event(terminal_check(TK_CHAR));
		}
	    }

	    monsters::monster_turns(gamestate);
	    gamestate->turns++;
	}	
    }
    terminal_close();
}
