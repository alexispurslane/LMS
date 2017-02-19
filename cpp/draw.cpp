#include "BearLibTerminal.h"

namespace draw
{
    void draw_screen(utils::GlobalState *gs)
    {
	terminal_clear();

	switch (gs->screen)
	{
	case utils::Intro:
	    draw_intro_screen(gs);
	case utils::Death:
	    draw_death_screen(gs);
	case utils::Game:
	    draw_game_screen(gs);
	case utils::CharacterSelection:
	    draw_charsel_screen(gs);
	}

	terminal_refresh();
    }

    void draw_intro_screen(utils::GlobalState *gs)
    {
	
    }
}
