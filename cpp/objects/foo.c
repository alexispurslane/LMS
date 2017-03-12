#include <stdio.h>
#include <yaml.h>

int main(void)
{
    FILE *fh = fopen("/Users/christopherdumas/AlchemySphere/cpp/objects/conf/items.yaml", "r");
    yaml_parser_t parser;
    yaml_event_t  event;   /* New variable */

    /* Initialize parser */
    if(!yaml_parser_initialize(&parser))
        fputs("Failed to initialize parser!\n", stderr);
    if(fh == NULL)
        fputs("Failed to open file!\n", stderr);

    /* Set input file */
    yaml_parser_set_input_file(&parser, fh);

    /* START new code */
    int indent = 0;
    do {
        if (!yaml_parser_parse(&parser, &event)) {
            printf("Parser error %d\n", parser.error);
            exit(EXIT_FAILURE);
        }

        printf("%*c", indent, ' ');
        switch(event.type)
        {
        case YAML_NO_EVENT: puts("No event!"); break;
            /* Stream start/end */
        case YAML_STREAM_START_EVENT: puts("STREAM START"); break;
        case YAML_STREAM_END_EVENT:   puts("STREAM END");   break;
            /* Block delimeters */
        case YAML_DOCUMENT_START_EVENT: puts("Start Document"); indent+=4; break;
        case YAML_DOCUMENT_END_EVENT:   puts("End Document"); indent-=4;  break;
        case YAML_SEQUENCE_START_EVENT: puts("Start Sequence"); indent+=4;break;
        case YAML_SEQUENCE_END_EVENT:   puts("End Sequence");  indent-=4; break;
        case YAML_MAPPING_START_EVENT:  puts("Start Mapping"); indent+=4; break;
        case YAML_MAPPING_END_EVENT:    puts("End Mapping");  indent-=4;  break;
            /* Data */
        case YAML_ALIAS_EVENT:  printf("Got alias (anchor %s)\n", event.data.alias.anchor); break;
        case YAML_SCALAR_EVENT: printf("Got scalar (value %s)\n", event.data.scalar.value); break;
        }
        if(event.type != YAML_STREAM_END_EVENT)
            yaml_event_delete(&event);
    } while(event.type != YAML_STREAM_END_EVENT);
    yaml_event_delete(&event);
    /* END new code */

    /* Cleanup */
    yaml_parser_delete(&parser);
    fclose(fh);
    return 0;
}
