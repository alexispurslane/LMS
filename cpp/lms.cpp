#include "BearLibTerminal.h"

#include <vector>
#include <cstdlib>
#include <ctime>
#include <string>
#include <map>
#include <cmath>
#include <random>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <memory>

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
    terminal_set("font: assets/font/IBMCGA16x16_gamestate_ro.png, size=16x16, codepage=437;");
    terminal_set("U+E000: assets/tileset8x8.png, size=8x8, align=top-left;");
    terminal_set("stone font: ../Media/Aesomatica_16x16_437.png, size=16x16, codepage=437, spacing=2x1, transparent=#FF00FF;");
    terminal_set("huge font: assets/font/VeraMono.ttf, size=20x40, spacing=2x2");
    terminal_composition(TK_ON);

    std::unique_ptr<terrain_map::TerrainMap> tmap{new terrain_map::TerrainMap(consts::WIDTH, consts::HEIGHT)};
    std::unique_ptr<character::Player> player{new character::Player(races::WARRIOR)};
    
    std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap, character::Player> > gamestate;
    gamestate->screen     = utils::ScreenState::Intro;
    gamestate->sidescreen = utils::SideScreenState::HUD;
    gamestate->map        = std::move(tmap);
    gamestate->player     = std::move(player);

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
	if (gamestate->player->health <= 0 && gamestate->screen != utils::ScreenState::Death)
	{
	    gamestate->screen = utils::ScreenState::Death;
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

		int map_x = std::max((double)0, gamestate->player->loc.x-floor(consts::WIDTH / 4));
		int map_y = std::max((double)0, gamestate->player->loc.y-floor(consts::HEIGHT / 2));
		area::Point cell{mx+map_x, my+map_y};

		auto e = (*gamestate->map)[cell];

		std::string id = "";
		switch (e.sme)
		{
		case dungeons::StaticMapElement::Floor:
		    id = "the floor";
		    break;
		case dungeons::StaticMapElement::Water:
		    id = "water";
		    break;
		case dungeons::StaticMapElement::Fire:
		    id = "flames";
		    break;
		case dungeons::StaticMapElement::GeneralObject:
		    if (!e.i.empty())
		    {
			id = "an " + e.i.front()->name;
		    }
		    else if (!e.m.empty())
		    {
			id = "a " + e.m.front()->name;
		    }
		    break;
		case dungeons::StaticMapElement::OpenDoor:
		    id = "an open door";
		    break;
		case dungeons::StaticMapElement::UpStairs:
		    id = "stairs leading up";
		    break;
		case dungeons::StaticMapElement::DownStairs:
		    id = "stairs leading down";
		    break;
		case dungeons::StaticMapElement::ClosedDoor:
		    id = "a closed door";
		    break;
		case dungeons::StaticMapElement::Wall:
		    switch (gamestate->map->area_at(cell).type)
		    {
		    case area::AreaType::Marble:
			id = "a beautiful marble slab wall";
			break;
		    case area::AreaType::Dirt:
			id = "a loose packed dirt wall";
			break;
		    case area::AreaType::Stone:
			id = "a moldy, lichen covered stone wall";
			break;
		    }
		    break;
		}

		gamestate->messages.push_back("You see " + id + " here.");
	    }
	    else if (event == TK_MOUSE_SCROLL)
	    {
		gamestate->message_offset += mouse_scroll_step * terminal_state(TK_MOUSE_WHEEL);
	    }
	    else
	    {
		if (gamestate->sidescreen == utils::SideScreenState::Inventory)
		{

		    // Because...You can't define variables in a switch statement
		    auto item = gamestate->player->inventory[gamestate->currentselection];
		    auto single_item = items::Item(item);
		    
		    switch (event)
		    {
		    case TK_UP:
			gamestate->currentselection--;
			gamestate->currentselection %= gamestate->player->inventory.size();
			break;
		    case TK_DOWN:
			gamestate->currentselection++;
			gamestate->currentselection %= gamestate->player->inventory.size();
			break;
		    case TK_D:
			item.count--;
			single_item.count = 1;
			(*gamestate->map)[gamestate->player->loc].i.push_back(std::make_shared<items::Item>(single_item));
			break;
		    case TK_RETURN:
			gamestate->player->inventory[gamestate->currentselection].equip(player);
			break;
		    case TK_ESCAPE:
			gamestate->player->inventory[gamestate->currentselection].dequip(player);
			break;
		    case TK_I:
			gamestate->sidescreen = utils::SideScreenState::HUD;
			break;
		    }
		}
		else if (gamestate->screen == utils::ScreenState::Intro)
		{
		    gamestate->screen = utils::ScreenState::CharacterSelection;
		}
		else if (gamestate->screen == utils::ScreenState::CharacterSelection)
		{
		    switch (event)
		    {
		    case TK_UP:
			gamestate->currentselection--;
			gamestate->currentselection %= 3;
			break;
		    case TK_DOWN:
			gamestate->currentselection++;
			gamestate->currentselection %= 3;
			break;
		    case TK_RETURN:
			auto racen = gamestate->currentselection-1;
			auto race = races::RACES[racen];
			gamestate->player->race = race;
			gamestate->difficulty = race.suggested_difficulty;
			gamestate->map->generate_new_map();
			gamestate->player->loc = gamestate->map->dungeon->player_start;
			gamestate->screen = utils::ScreenState::Game;
			break;
		    }
		}
		else if (gamestate->screen == utils::ScreenState::Game)
		{
		    auto b = consts::PLAYER_HANDLE.begin();
		    auto e = consts::PLAYER_HANDLE.end();
		    if (std::find_if(b, e, [](char x) { return x == terminal_check(TK_CHAR); }) != e)
		    {
			gamestate->player->handle_event(terminal_check(TK_CHAR));
		    }
		    else
		    {
			switch (terminal_check(TK_CHAR))
			{
			case 'i':
			    if (gamestate->sidescreen == utils::SideScreenState::Inventory)
			    {
				gamestate->sidescreen = utils::SideScreenState::HUD;
			    }
			    else
			    {
				gamestate->sidescreen = utils::SideScreenState::Inventory;
			    }
			    break;
			case 'm':
			    if (gamestate->sidescreen == utils::SideScreenState::Skills)
			    {
				gamestate->sidescreen = utils::SideScreenState::HUD;
			    }
			    else
			    {
				gamestate->sidescreen = utils::SideScreenState::Skills;
			    }
			    break;
			default:
			    break;
			}
		    }
		}
	    }

	    monsters::monster_turns(gamestate);
	    gamestate->turns++;
	}	
    }
    terminal_close();
}
