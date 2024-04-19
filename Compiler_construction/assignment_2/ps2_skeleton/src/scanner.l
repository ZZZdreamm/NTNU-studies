%{
#include <vslc.h>
// The tokens defined in parser.y
#include "parser.h"

// parser.h contains some unused functions, ignore that
#pragma GCC diagnostic ignored "-Wunused-function"
%}
%option noyywrap
%option array
%option yylineno

WHITESPACE [\ \t\v\r\n]
COMMENT \/\/[^\n]+
QUOTED \"([^\"\n]|\\\")*\"

NUMBER [0-9]+
IDENTIFIER  [A-Za-z_][A-Za-z0-9_]*
OPENBLOCK "begin"
CLOSEBLOCK "end"



%%
{WHITESPACE}+           { /* Eliminate whitespace */ }
{COMMENT}               { /* Eliminate comments */ }
{QUOTED}                { return STRING; }
"func"                  { return FUNC; }
{OPENBLOCK}             { return OPENBLOCK; }
{CLOSEBLOCK}            { return CLOSEBLOCK; }
"return"                { return RETURN; }
"print"                 { return PRINT; }
"break"                 { return BREAK; }
"if"                    { return IF; }
"then"                  { return THEN; }
"else"                  { return ELSE; }
"while"                 { return WHILE; }
"do"                    { return DO; }
"var"                   { return VAR; }
{NUMBER}                { return NUMBER; }
{IDENTIFIER}            { return IDENTIFIER; }

  /* Unknown chars get returned as single char tokens */
.                       { return yytext[0]; }
%%
