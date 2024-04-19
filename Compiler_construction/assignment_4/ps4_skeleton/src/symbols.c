#include <vslc.h>

/* Global symbol table and string list */
symbol_table_t *global_symbols;
char **string_list;
size_t string_list_len;
size_t string_list_capacity;

static void find_globals ( void );
static void bind_names ( symbol_table_t *local_symbols, node_t *root );
static void print_symbol_table ( symbol_table_t *table, int nesting );
static void destroy_symbol_tables ( symbol_table_t *table );

static size_t add_string ( char* string );
static void print_string_list ( void );
static void destroy_string_list ( void );

/* External interface */

/* Creates a global symbol table, and local symbol tables for each function.
 * While building the symbol tables:
 *  - All usages of symbols are bound to their symbol table entries.
 *  - All strings are entered into the string_list
 */
void create_tables ( void )
{
    find_globals();
    for (size_t i = 0; i < root->n_children; i++)
    {
        node_t *child = root->children[i];
        if (child->type == FUNCTION) {
            symbol_t *symbol = symbol_hashmap_lookup(global_symbols->hashmap, (char*)child->children[0]->data);
            bind_names(symbol->function_symtable, child->children[2]); // Bind names in the function body starting from highest lvl block
        }
    }

}

/* Prints the global symbol table, and the local symbol tables for each function.
 * Also prints the global string list.
 * Finally prints out the AST again, with bound symbols.
 */
void print_tables ( void )
{
    print_symbol_table ( global_symbols, 0 );
    printf("\n == STRING LIST == \n");
    print_string_list ();
    printf("\n == BOUND SYNTAX TREE == \n");
    print_syntax_tree ();
}

/* Destroys all symbol tables and the global string list */
void destroy_tables ( void )
{
    destroy_symbol_tables ( global_symbols);
    destroy_string_list ( );
}


// Find the parent of the IDENTIFIER_DATA node (used in global declaration node)
node_t *find_identifiers_parent(node_t *node) {
    if (node->children[0]->type == IDENTIFIER_DATA) {
        return node;
    } else {
        for (size_t i = 0; i < node->n_children; i++) {
            node_t *child = node->children[i];
            node_t *result = find_identifiers_parent(child);
            if (result != NULL) {
                return result;
            }
        }
    }
    return NULL;
}

/* Internal matters */

/* Goes through all global declarations in the syntax tree, adding them to the global symbol table.
 * When adding functions, local symbol tables are created, and symbols for the functions parameters are added.
 */
static void find_globals ( void )
{
    global_symbols = symbol_table_init ( );

    for (size_t i = 0; i < root->n_children; i++)
    {
        node_t *child = root->children[i];

        if (child->type == FUNCTION) {
            symbol_table_t *local_symbols = symbol_table_init();
            local_symbols->hashmap->backup = global_symbols->hashmap;

            node_t *identifier_data_node = child->children[0];
            symbol_t *symbol = malloc(sizeof(symbol_t));
            symbol->name = (char*)identifier_data_node->data;
            symbol->type = SYMBOL_FUNCTION;
            symbol->function_symtable = local_symbols;
            symbol->node = identifier_data_node;

            node_t *parameters_parent = child->children[1];
            for (size_t i = 0; i < parameters_parent->n_children; i++)
            {
                node_t *parameter_data_node = parameters_parent->children[i];
                symbol_t *symbol = malloc(sizeof(symbol_t));
                symbol->name = (char*)parameter_data_node->data;
                symbol->type = SYMBOL_PARAMETER;
                symbol->function_symtable = local_symbols;
                symbol->node = parameter_data_node;
                insert_result_t result = symbol_table_insert(local_symbols, symbol);
                if (result == INSERT_COLLISION) {
                    printf("In function: Symbol '%s' already exists in the local symbol table.\n", (char*)child->data);
                }
            }

            // Add the symbol to the global symbol table
            insert_result_t result = symbol_table_insert(global_symbols, symbol);
            if (result == INSERT_COLLISION) {
                printf("Function: Symbol '%s' already exists in the global symbol table.\n", (char*)child->data);
            }

        }else if (child->type == GLOBAL_DECLARATION) {
            // Add the symbol to the global symbol table
            node_t *identifiers_parent = find_identifiers_parent(child);
            symtype_t type = identifiers_parent->type == ARRAY_INDEXING ? SYMBOL_GLOBAL_ARRAY : SYMBOL_GLOBAL_VAR;
            for (size_t i = 0; i < identifiers_parent->n_children; i++)
            {
                node_t *identifier_data_node = identifiers_parent->children[i];
                if(identifier_data_node->type == IDENTIFIER_DATA){
                    symbol_t *symbol = malloc(sizeof(symbol_t));
                    symbol->name = (char*)identifier_data_node->data;
                    symbol->type = type;
                    symbol->function_symtable = NULL;
                    symbol->node = identifier_data_node;
                    insert_result_t result = symbol_table_insert(global_symbols, symbol);
                    if (result == INSERT_COLLISION) {
                        printf("In global declaration: Symbol '%s' already exists in the global symbol table.\n", (char*)child->data);
                    }
                }
            }
        }
    }
}


// If the node is an IDENTIFIER_DATA node with any ancestor being statement node,
// bind it to the symbol it references instead of creating new symbol.
void bind_statement_identifier_data(node_t *node, symbol_table_t *local_symbols) {
    if (node->type == IDENTIFIER_DATA) {
        symbol_t *symbol = symbol_hashmap_lookup(local_symbols->hashmap, (char*)node->data);
        node->symbol = symbol;
    }
    else if(node->type == STRING_DATA){
        size_t position = add_string(node->data);
        node->type = STRING_LIST_REFERENCE;
        node->data = (void*) position;
    }
    else {
        for (size_t i = 0; i < node->n_children; i++) {
            bind_statement_identifier_data(node->children[i], local_symbols);
        }
    }
}


/* A recursive function that traverses the body of a function, and:
 *  - Adds variable declarations to the function's local symbol table.
 *  - Pushes and pops local variable scopes when entering and leaving blocks.
 *  - Binds all other IDENTIFIER_DATA nodes to the symbol it references.
 *  - Moves STRING_DATA nodes' data into the global string list,
 *    and replaces the node with a STRING_LIST_REFERENCE node.
 *    This node's data is a pointer to the char* stored in the string list.
 */
static void bind_names ( symbol_table_t *local_symbols, node_t *node )
{
    if (node->type == IDENTIFIER_DATA) {
        symbol_t *symbol = malloc(sizeof(symbol_t));
        symbol->name = (char*)node->data;
        symbol->type = SYMBOL_LOCAL_VAR;
        symbol->function_symtable = local_symbols;
        symbol->node = node;
        insert_result_t result = symbol_table_insert(local_symbols, symbol);
        if (result == INSERT_COLLISION) {
            printf("Local var in function: Symbol '%s' already exists in the local symbol table.\n", (char*)node->data);
        }

    } else if (node->type == STRING_DATA) { /// INPUT STRING TO STRING LIST
        size_t position = add_string(node->data);
        node->type = STRING_LIST_REFERENCE;
        node->data = (void*) position;
    }
    else if (node->type >= 6 && node->type <= 11) {
        bind_statement_identifier_data(node, local_symbols);
    } else if (node->type == BLOCK){
        symbol_hashmap_t *block_scope = symbol_hashmap_init();
        block_scope->backup = local_symbols->hashmap;
        local_symbols->hashmap = block_scope;

        for (size_t i = 0; i < node->n_children; i++) {
            bind_names(local_symbols, node->children[i]);
        }

        local_symbols->hashmap = block_scope->backup;
        symbol_hashmap_destroy(block_scope);

    } else {
        for (size_t i = 0; i < node->n_children; i++) {
            bind_names(local_symbols, node->children[i]);
        }
    }
}




/* Prints the given symbol table, with sequence number, symbol names and types.
 * When printing function symbols, its local symbol table is recursively printed, with indentation.
 */
static void print_symbol_table ( symbol_table_t *table, int nesting )
{
    if (table == NULL) {
        printf("Error: Symbol table is NULL.\n");
        return;
    }
    for (size_t i = 0; i < table->n_symbols; i++) {
        symbol_t *symbol = table->symbols[i];

        for (int j = 0; j < nesting; j++) {
            printf("    ");
        }
        printf("%zu: %s(%s)\n", symbol->sequence_number, SYMBOL_TYPE_NAMES[symbol->type], symbol->name);
        if(symbol->type == SYMBOL_FUNCTION && symbol->function_symtable != NULL){
            print_symbol_table(symbol->function_symtable, nesting + 1);
        }
    }
}



/* Frees up the memory used by the global symbol table, all local symbol tables, and their symbols */
static void destroy_symbol_tables ( symbol_table_t *table )
{
    if (table) {
        for (size_t i = 0; i < table->n_symbols; i++) {
            symbol_t *symbol = table->symbols[i];
            if(symbol->type == SYMBOL_FUNCTION && symbol->function_symtable != NULL){
                destroy_symbol_tables(symbol->function_symtable);
            }
            if (symbol) {
                free(symbol);
            }
        }
        if (table->hashmap != NULL) {
            symbol_hashmap_destroy(table->hashmap);
        }
        free(table->symbols);
        free(table);
    }
}

/* Adds the given string to the global string list, resizing if needed.
 * Takes ownership of the string, and returns its position in the string list.
 */
static size_t add_string ( char *string )
{
    // TODO: Write a helper function you can use during bind_names(),
    // to easily add a string into the dynamically growing string_list
    if (string_list_len + 1 >= string_list_capacity) {
        string_list_capacity = string_list_capacity * 2 + 8;
        string_list = realloc(string_list, string_list_capacity * sizeof(char*));
    }
    string_list[string_list_len] = string;
    string_list_len++;

    return string_list_len - 1;

}

/* Prints all strings added to the global string list */
static void print_string_list ( void )
{
    for (int i = 0; i < string_list_len; i++) {
        printf("%d: %s\n", i, string_list[i]);
    }
}

/* Frees all strings in the global string list, and the string list itself */
static void destroy_string_list ( void )
{
    // TODO: Called during cleanup, free strings, and the memory used by the string list itself
    for (int i = 0; i < string_list_len; i++) {
        free(string_list[i]);
    }

    free(string_list);
    string_list_len = 0;
}
