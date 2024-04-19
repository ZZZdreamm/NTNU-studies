#define NODETYPES_IMPLEMENTATION
#include <vslc.h>

// Global root for abstract syntax tree
node_t *root;

// Declarations of internal functions, defined further down
static void node_print ( node_t *node, int nesting );
static void destroy_subtree ( node_t *discard );
static node_t* simplify_subtree ( node_t *node );

// Outputs the entire syntax tree to the terminal
void print_syntax_tree ( void )
{
    if ( getenv("GRAPHVIZ_OUTPUT") != NULL )
        graphviz_node_print ( root );
    else
        node_print ( root, 0 );
}

// Cleans up the entire syntax tree
void destroy_syntax_tree ( void )
{
    destroy_subtree ( root );
    root = NULL;
}

// Modifies the syntax tree, performing constant folding where possible
void simplify_tree ( void )
{
    root = simplify_subtree( root );
}

// Initialize a node with type, data, and children
node_t* node_create ( node_type_t type, void *data, size_t n_children, ... )
{
    node_t* result = malloc ( sizeof ( node_t ) );

    // Initialize every field in the struct
    *result = (node_t) {
        .type = type,
        .n_children = n_children,
        .children = (node_t **) malloc ( n_children * sizeof ( node_t * ) ),

        .data = data,
    };

    // Read each child node from the va_list
    va_list child_list;
    va_start ( child_list, n_children );
    for ( size_t i = 0; i < n_children; i++ )
        result->children[i] = va_arg ( child_list, node_t * );
    va_end ( child_list );

    return result;
}

// Append an element to the given LIST node, returns the list node
node_t* append_to_list_node ( node_t* list_node, node_t* element )
{
    assert ( list_node->type == LIST );

    // Calculate the minimum size of the new allocation
    size_t min_allocation_size = list_node->n_children + 1;

    // Round up to the next power of two
    size_t new_allocation_size = 1;
    while ( new_allocation_size < min_allocation_size ) new_allocation_size *= 2;

    // Resize the allocation
    list_node->children = realloc ( list_node->children, new_allocation_size * sizeof(node_t *) );

    // Insert the new element and increase child count by 1
    list_node->children[list_node->n_children] = element;
    list_node->n_children++;

    return list_node;
}

// Prints out the given node and all its children recursively
static void node_print ( node_t *node, int nesting )
{
    printf ( "%*s", nesting, "" );

    if ( node == NULL )
    {
        printf ( "(NULL)\n");
        return;
    }

    printf ( "%s", node_strings[node->type] );

    // For nodes with extra data, print the data with the correct type
    if ( node->type == IDENTIFIER_DATA ||
         node->type == EXPRESSION ||
         node->type == RELATION ||
         node->type == STRING_DATA)
    {
        printf ( "(%s)", (char *) node->data );
    }
    else if ( node->type == NUMBER_DATA )
    {
        printf ( "(%ld)", *(int64_t *) node->data );
    }

    putchar ( '\n' );

    // Recursively print children, with some more indentation
    for ( size_t i = 0; i < node->n_children; i++ )
        node_print ( node->children[i], nesting + 1 );
}

// Frees the memory owned by the given node, but does not touch its children
static void node_finalize ( node_t *discard )
{
    if ( discard == NULL )
        return;

    // Only free data if the data field is owned by the node
    switch ( discard->type )
    {
        case IDENTIFIER_DATA:
        case NUMBER_DATA:
        case STRING_DATA:
            free ( discard->data );
        default:
            break;
    }
    free ( discard->children );
    free ( discard );
}

// Recursively frees the memory owned by the given node, and all its children
static void destroy_subtree ( node_t *discard )
{
    if ( discard == NULL )
        return;

     for ( size_t i = 0; i < discard->n_children; i++ )
        destroy_subtree ( discard->children[i] );
     node_finalize ( discard );
}




static int is_operator(const char* operator) {
    return strcmp(operator, "+") == 0 || strcmp(operator, "-") == 0 ||
           strcmp(operator, "*") == 0 || strcmp(operator, "/") == 0 ||
           strcmp(operator, "<<") == 0 || strcmp(operator, ">>") == 0;
}

// Helper function to perform the appropriate operation based on the operator
static int64_t perform_operation(const char* operator, int64_t a, int64_t b) {
    if (strcmp(operator, "+") == 0) {
        return a + b;
    } else if (strcmp(operator, "-") == 0) {
        return a - b;
    } else if (strcmp(operator, "*") == 0) {
        return a * b;
    } else if (strcmp(operator, "/") == 0) {
        return a / b;
    } else if (strcmp(operator, "<<") == 0) {
        return  a << b;
    } else if (strcmp(operator, ">>") == 0) {
        return a >> b;
    }
    // Invalid operator
    return 0;
}

// Recursively replaces EXPRESSION nodes representing mathematical operations
// where all operands are known integer constants
static node_t* constant_fold_node ( node_t *node )
{
    if (node->type != EXPRESSION) {
        return node;
    }

    for (size_t i = 0; i < node->n_children; i++) {
        if (node->children[i]->type != NUMBER_DATA) {
            return node;
        }
    }

    const char* operator = (const char*)node->data;

    if (!is_operator(operator)) {
        return node;
    }


    int64_t result = *(int64_t*)node->children[0]->data;
    if(node->n_children == 1){
        result = perform_operation(operator, 0, result);
    }

    for (size_t i = 1; i < node->n_children; i++) {
        int64_t operand = *(int64_t*)node->children[i]->data;
        result = perform_operation(operator, result, operand);
    }

    destroy_subtree(node);

    node_t* folded_node = malloc(sizeof(node_t));
    folded_node->type = NUMBER_DATA;
    folded_node->children = NULL;
    folded_node->n_children = 0;
    folded_node->data = malloc(sizeof(int64_t));
    *(int64_t*)folded_node->data = result;
    folded_node->symbol = NULL;

    return folded_node;
}

// Recursively replaces multiplication and division by powers of two, with bitshifts
static node_t* peephole_optimize_node ( node_t* node )
{
    if (node->type == EXPRESSION && (strcmp(node->data, "*") == 0 || strcmp(node->data, "/") == 0)) {
        int factor = *((int*)node->children[1]->data);
        if (factor != 1 && (factor != 0) && ((factor & (factor - 1)) == 0)) {
            int power = 0;
            while (factor > 1) {
                power++;
                factor >>= 1;
            }

            char* operator = (char*)node->data;
            switch (operator[0]) {
                case '*':
                    node->data = strdup("<<");
                    *(int64_t*)node->children[1]->data = power;
                    break;
                case '/':
                    node->data = strdup(">>");
                    *(int64_t*)node->children[1]->data = power;
                    break;
                default:
                    return node;
            }
        }else if(factor == 1) {
            node_t* child = node->children[0];
            node_finalize(node);
            return child;
        }
    }

    return node;
}

static node_t* simplify_subtree( node_t* node )
{
    if (node == NULL)
        return NULL;

    for (size_t i = 0; i < node->n_children; i++)
    {
        node->children[i] = simplify_subtree(node->children[i]);
    }

    node = constant_fold_node(node);
    node = peephole_optimize_node(node);

    return node;
}



