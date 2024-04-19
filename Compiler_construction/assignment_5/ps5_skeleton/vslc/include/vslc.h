#ifndef VSLC_H
#define VSLC_H
/* Definition of the tree node type, and functions for handling the parse tree */
#include "tree.h"
/* Definition of the symbol table, and functions for building it */
#include "symbols.h"

#include <assert.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Function for generating machine code, in generator.c */
void generate_program ( void );

/* The main driver function of the parser generated by bison */
int yyparse ();

/* A "hidden" cleanup function in flex */
int yylex_destroy ();

#endif // VSLC_H
