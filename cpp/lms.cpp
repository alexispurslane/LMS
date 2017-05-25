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
    terminal_set("font: assets/font/IBMCGA16x16_gs_ro.png, size=16x16, codepage=437;");
    terminal_set("U+E000: assets/tileset8x8.png, size=8x8, align=top-left;");
    terminal_set("stone font: ../Media/Aesomatica_16x16_437.png, size=16x16, codepage=437, spacing=2x1, transparent=#FF00FF;");
    terminal_set("huge font: assets/font/VeraMono.ttf, size=20x40, spacing=2x2");
    terminal_composition(TK_ON);

    std::shared_ptr<utils::GlobalState<terrain_map::TerrainMap, character::Player> > gs;
    gs->screen     = utils::ScreenState::Intro;
    gs->sidescreen = utils::SideScreenState::HUD;
    gs->map        = {consts::WIDTH, consts::HEIGHT};
    gs->player     = {races::WARRIOR};
    items::load();
    monsters::load();

    std::ifstream infile(".gamescores");
    std::string line;
    while (std::getline(infile, line))
    {
        std::istringstream iss(line);
        int score = 0;
        if (!(iss >> score)) { break; } // error
        gs->scores.push_back(score);
    }

    while (true)
    {
        // Update Screen
        if (gs->player.health <= 0 && gs->screen != utils::ScreenState::Death)
        {
            gs->screen = utils::ScreenState::Death;
        }
        draw::draw_screen(gs);

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

                int map_x = std::max((double)0, gs->player.loc.x-floor(consts::WIDTH / 4));
                int map_y = std::max((double)0, gs->player.loc.y-floor(consts::HEIGHT / 2));
                area::Point cell{mx+map_x, my+map_y};

                auto e = gs->map[cell];

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
                    switch (gs->map.area_at(cell).type)
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
                default:
                    id = "unknown";
                    break;
                }

                gs->messages.insert(gs->messages.begin(),
                                    "You see " + id + " here.");
            }
            else if (event == TK_MOUSE_SCROLL)
            {
                gs->message_offset += mouse_scroll_step * terminal_state(TK_MOUSE_WHEEL);
            }
            else
            {
                if (gs->sidescreen == utils::SideScreenState::Inventory)
                {

                    // Because...You can't define variables in a switch statement
                    auto item = &gs->player.inventory[gs->currentselection];
                    auto single_item = gs->player.inventory[gs->currentselection];

                    switch (event)
                    {
                    case TK_UP:
                        gs->currentselection--;
                        gs->currentselection %= gs->player.inventory.size();
                        break;
                    case TK_DOWN:
                        gs->currentselection++;
                        gs->currentselection %= gs->player.inventory.size();
                        break;
                    case TK_D:
                        item->count--;
                        single_item.count = 1;
                        gs->map[gs->player.loc].i.push_back(std::make_shared<items::Item>(single_item));
                        break;
                    case TK_RETURN:
                        gs->player.inventory[gs->currentselection].equip(gs->player);
                        break;
                    case TK_ESCAPE:
                        gs->player.inventory[gs->currentselection].dequip(gs->player);
                        break;
                    case TK_I:
                        gs->sidescreen = utils::SideScreenState::HUD;
                        break;
                    }
                }
                else if (gs->screen == utils::ScreenState::Intro)
                {
                    gs->screen = utils::ScreenState::CharacterSelection;
                }
                else if (gs->screen == utils::ScreenState::CharacterSelection)
                {
                    switch (event)
                    {
                    case TK_UP:
                        gs->currentselection--;
                        gs->currentselection %= 3;
                        break;
                    case TK_DOWN:
                        gs->currentselection++;
                        gs->currentselection %= 3;
                        break;
                    case TK_RETURN:
                        auto racen = gs->currentselection-1;
                        auto race = races::RACES[racen];
                        gs->player.race = race;
                        gs->difficulty = race.suggested_difficulty;
                        gs->map.generate_new_map();
                        gs->player.loc = gs->map.dungeon.player_start;
                        gs->screen = utils::ScreenState::Game;
                        break;
                    }
                }
                else if (gs->screen == utils::ScreenState::Game)
                {
                    int allotted = 10;
                    while (allotted > 0)
                    {
                        char character = terminal_check(TK_CHAR);
                        if (std::find(consts::PLAYER_HANDLE.begin(),
                                      consts::PLAYER_HANDLE.end(),
                                      character) != consts::PLAYER_HANDLE.end())
                        {
                            allotted -= gs->player.handle_event(gs, character);
                        }
                        else
                        {
                            allotted -= 10;
                            switch (character)
                            {
                            case 'i':
                                if (gs->sidescreen == utils::SideScreenState::Inventory)
                                {
                                    gs->sidescreen = utils::SideScreenState::HUD;
                                }
                                else
                                {
                                    gs->sidescreen = utils::SideScreenState::Inventory;
                                }
                                break;
                            case 'm':
                                if (gs->sidescreen == utils::SideScreenState::Skills)
                                {
                                    gs->sidescreen = utils::SideScreenState::HUD;
                                }
                                else
                                {
                                    gs->sidescreen = utils::SideScreenState::Skills;
                                }
                                break;
                            default:
                                break;
                            }
                        }
                    }
                }
            }

            monsters::monster_turns(gs);
            gs->turns++;
        }
    }
    terminal_close();
}
