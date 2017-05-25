#include <stdio.h>
#include <yaml.h>
#include <iomanip>
#include <vector>
#include <string>
#include <map>
#include <string>
#include <sstream>
#include <iostream>

bool is_number(const std::string& s)
{
    return !s.empty() && std::find_if(s.begin(),
                                      s.end(), [](char c) { return !std::isdigit(c); }) == s.end();
}

typedef std::string Action;
std::map<std::string, Action> ACTIONS;

class Monster
{
public:
    std::string name;
    std::vector<int> tiles;
    int tile;
    std::string color;
    int speed;
    int health;
    int attack;
    bool aggressive;
    Action action;
    bool ranged;
};

std::map<std::string, Monster> MONSTERS;

int main(void)
{
    FILE *fh = fopen("/Users/christopherdumas/AlchemySphere/cpp/objects/conf/monsters.yaml", "r");
    yaml_parser_t parser;
    yaml_event_t  event;   /* New variable */

    /* Initialize parser */
    if(!yaml_parser_initialize(&parser))
    {
        fputs("Failed to initialize parser!\n", stderr);
    }
    if(fh == NULL)
    {
        fputs("Failed to open file!\n", stderr);
    }

    /* Set input file */
    yaml_parser_set_input_file(&parser, fh);

    /* START\n new code */
    enum class MonsterValType
    {
        Str, Bool, Int, IntVector, Empty
    };

    struct MonsterVal
    {
        MonsterValType type;
        std::string str;
        std::vector<int> iv;
        int i = 0;
        bool b = false;
    };

    typedef std::map<std::string,  MonsterVal> MonsterMap;

    int mapping_level = 0;
    enum MappingLevels { TypeMapping = 1, Mapping = 2, PropertyMapping = 3 };

    int sequence_level = 0;
    enum SequenceLevels { TypeOfMonster = 1, Tiles = 2 };

    std::vector<MonsterMap> monsters;
    MonsterMap monster;
    std::string key = "";

    MonsterVal val;
    val.type = MonsterValType::Empty;

    do
    {
        if (!yaml_parser_parse(&parser, &event))
        {
            printf("Parser error %d\n", parser.error);
            exit(EXIT_FAILURE);
        }

        switch(event.type)
        {
        case YAML_SEQUENCE_START_EVENT:
            sequence_level++;
            if (sequence_level == Tiles && key == "tiles")
            {
                monster.erase("tile");
                key = "tiles";
                val.type = MonsterValType::IntVector;
                val.iv = std::vector<int>();
            }
            break;

        case YAML_SEQUENCE_END_EVENT:
            if (sequence_level == Tiles)
            {
                monster[key] = val;
                val.type = MonsterValType::Empty;
                key = "";
            }
            sequence_level--;
            break;

        case YAML_MAPPING_START_EVENT:
            mapping_level++;
            break;

        case YAML_MAPPING_END_EVENT:
            mapping_level--;
            switch (mapping_level)
            {
            case Mapping:
                // Monster::name (in this case in pre-postprocessing map)
                // is always a string (hopefully)
                monsters.push_back(monster);
                monster = MonsterMap();
                break;
            }
            break;

            /* Data */
        case YAML_SCALAR_EVENT:
            std::string strval(reinterpret_cast<char*>(event.data.scalar.value));
            if (sequence_level == Tiles)
            {
                std::stringstream convert(strval);
                unsigned int value;
                convert >> std::hex >> value;
                val.iv.push_back(value);
            }
            else if (mapping_level == PropertyMapping)
            {
                if (key == "")
                {
                    key = strval;
                }
                else if (val.type == MonsterValType::Empty)
                {
                    if (is_number(strval))
                    {
                        std::stringstream convert(strval);
                        convert >> val.i;
                        val.type = MonsterValType::Int;
                    }
                    else if (strval == "True")
                    {
                        val.type = MonsterValType::Bool;
                        val.b = true;
                    }
                    else if (strval == "False")
                    {
                        val.type = MonsterValType::Bool;
                        val.b = false;
                    }
                    else
                    {
                        val.str = strval;
                        val.type = MonsterValType::Str;
                    }
                }

                if (val.type != MonsterValType::Empty && key != "")
                {
                    monster[key] = val;
                    key = "";
                    val.type = MonsterValType::Empty;
                }
            }
            else if (mapping_level == TypeMapping)
            {
                val.type = MonsterValType::Str;
                val.str = strval;
                monster["broad_category"] = val;
                val.type = MonsterValType::Empty;
            }
            else if (mapping_level == Mapping)
            {
                std::transform(strval.begin(), strval.end(), strval.begin(),
                               [](char ch) {
                                   return ch == ' ' ? '_' : toupper(ch);
                               });

                val.type = MonsterValType::Str;
                val.str = strval;
                monster["name"] = val;
                val.type = MonsterValType::Empty;
            }
            break;
        }
        if(event.type != YAML_STREAM_END_EVENT)
        {
            yaml_event_delete(&event);
        }
    }
    while(event.type != YAML_STREAM_END_EVENT);

    for (auto mmap : monsters)
    {
        Monster mon;
        mon.name = mmap["name"].str;
        if (mmap.find("tiles") != mmap.end())
        {
            mon.tiles = mmap["tiles"].iv;
        }
        else
        {
            mon.tiles = {mmap["tile"].i};
        }
        mon.color = /*color_from_name*/(mmap["color"].str/*.c_str()*/);
        mon.speed = mmap["speed"].i;
        mon.health = mmap["health"].i;
        mon.attack = mmap["attack"].i;
        if (mmap.find("agressive") != mmap.end() && mmap["aggressive"].b)
        {
            mon.aggressive = true;
        }
        else
        {
            mon.aggressive = false;
        }
        if (mmap.find("ranged") != mmap.end() && mmap["ranged"].b)
        {
            mon.ranged = true;
        }
        else
        {
            mon.ranged = false;
        }
        /*mon.action = ACTIONS[mmap["action"].str];*/
        MONSTERS[mon.name] = mon;
    }

    yaml_event_delete(&event);
    /* END\n new code */

    /* Cleanup */
    yaml_parser_delete(&parser);
    fclose(fh);

    return 0;
}
