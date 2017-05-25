#include "items.hpp"
#include "../lib/utils.hpp"
#include <yaml.h>
#include <stdio.h>
#include <stdexcept>

enum class ItemValType
{
    String, StringVector, Integer, Empty
};

struct ItemVal
{
    ItemValType type;
    std::string str;
    std::vector<std::string> strv;
    int i = 0;
};

typedef std::map<std::string,  ItemVal> ItemMap;

void items::load()
{
    FILE *fh = fopen("/Users/christopherdumas/AlchemySphere/cpp/objects/conf/items.yaml", "r");
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

    /* START new code */
    int mapping_level = 0;
    int sequence_level = 0;
    enum MappingLevels
    {
        TypeMapping = 1,
        Mapping = 2,
        PropertyMapping = 3
    };

    enum SequenceLevels
    {
        TypeOfItem = 1,
        Categories = 2
    };

    std::vector<ItemMap> items;
    ItemMap item;
    std::string key = "";

    ItemVal val;
    val.type = ItemValType::Empty;

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
            if (sequence_level == Categories)
            {
                if (key == "category")
                {
                    val.type = ItemValType::StringVector;
                    val.strv = std::vector<std::string>();
                }
            }
            sequence_level++;
            break;

        case YAML_SEQUENCE_END_EVENT:
            if (sequence_level == Categories)
            {
                item[key] = val;
                val.type = ItemValType::Empty;
                val.strv = std::vector<std::string>();
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
                // Item::name (in this case in pre-postprocessing map)
                // is always a string (hopefully)
                items.push_back(item);
                item = std::map<std::string, ItemVal>();
                break;
            }
            break;

            /* Data */
        case YAML_SCALAR_EVENT:
            std::string strval(reinterpret_cast<char*>(event.data.scalar.value));
            if (sequence_level == Categories)
            {
                val.strv.push_back(strval);
            }
            else if (mapping_level == PropertyMapping)
            {
                if (key == "")
                {
                    key = strval;
                }
                else if (val.type == ItemValType::Empty)
                {
                    if (utils::is_number(strval))
                    {
                        std::stringstream convert(strval);
                        convert >> val.i;
                        val.type = ItemValType::Integer;
                    }
                    else
                    {
                        val.str = strval;
                        val.type = ItemValType::String;
                    }
                }

                if (val.type != ItemValType::Empty && key != "")
                {
                    item[key] = val;
                    key = "";
                    val.type = ItemValType::Empty;
                }
            }
            else if (mapping_level == TypeMapping)
            {
                val.type = ItemValType::String;
                val.str = strval;
                item["broad_category"] = val;
                val.type = ItemValType::Empty;
            }
            else if (mapping_level == Mapping)
            {
                std::transform(strval.begin(), strval.end(), strval.begin(), [](char ch) {
                        return ch == ' ' ? '_' : toupper(ch);
                    });

                val.type = ItemValType::String;
                val.str = strval;
                item["name"] = val;
                val.type = ItemValType::Empty;
            }
            break;
        }
        if(event.type != YAML_STREAM_END_EVENT)
        {
            yaml_event_delete(&event);
        }
    }
    while(event.type != YAML_STREAM_END_EVENT);

    for (auto item_map : items)
    {
        Item item;

        WBC ibc = WBC::Light; // Random, doesn't matter.
        if (item_map["broad_category"].str == "weapon")
        {
            ibc = WBC::Weapon;
        }
        else if (item_map["broad_category"].str == "armor")
        {
            ibc = WBC::Armor;
        }
        else if (item_map["broad_category"].str == "ranged weapon")
        {
            ibc = WBC::RangedWeapon;
        }
        else if (item_map["broad_category"].str == "missle")
        {
            ibc = WBC::Missle;
        }
        else if (item_map["broad_category"].str == "light")
        {
            ibc = WBC::Light;
        }

        // All Items have these properties
        item.name = item_map["name"].str;
        item.categories = item_map["category"].strv;
        item.c = std::stoi(item_map["char"].str.c_str());
        item.color = color_from_name(item_map["color"].str);
        item.weight = item_map["weight"].i;
        item.probability = item_map["probability"].i;
        item.broad_category = ibc;

        switch (ibc)
        {
        case WBC::Weapon:
            item.handedness = item_map["handedness"].i;
            item.attack = item_map["attack"].i;
            break;

        case WBC::Armor:
            if (item_map.find("defence") != item_map.end())
            {
                item.defence = item_map["defence"].i;
            }
            break;

        case WBC::RangedWeapon:
            item.range = item_map["range"].i;
            item.load_speed = item_map["load_speed"].i;
            break;

        case WBC::Missle:
            item.hit = item_map["hit"].i;
            item.accuracy = item_map["accuracy"].i;
            break;

        case WBC::Light:
            item.radius = item_map["radius"].i;
            item.lasts = item_map["lasts"].i;
            break;

        case WBC::Food:
            item.nutrition = item_map["nutrition"].i;
            break;
        }
        ITEMS[item_map["name"].str] = std::move(item);
    }

    yaml_event_delete(&event);
    /* END new code */

    /* Cleanup */
    yaml_parser_delete(&parser);
    fclose(fh);
}
