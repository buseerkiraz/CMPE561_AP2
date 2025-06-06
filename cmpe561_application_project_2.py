# -*- coding: utf-8 -*-
"""CMPE561 Application Project 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K81mc6v4JeExSeTu8oPEKAPOiZWh5p6-

This project is for CMPE561 (Natural Language Processing) Master's course at Boğaziçi University.
It implements a Context-Free Grammar (CFG) based syntactic parser using the CKY (Cocke-Kasami-Younger)
parsing algorithm, with a full pipeline that supports lexicon integration, grammar normalization, and
parse table construction for input sentences.

The system begins by defining a set of CFG grammar rules (`GrammarRule`) and importing a lexicon
from an Excel sheet using the `LexiconRule` class. Lexical rules are parsed and stored as a dictionary
that maps POS tags to their corresponding word lists. These lexical entries are used to connect
terminal symbols (words) to non-terminal categories (e.g., NN, VB, RB).

To make the grammar compatible with the CKY algorithm, which requires Chomsky Normal Form (CNF),
the project includes a `CNFConverter` class. This class handles:
- Converting rules with more than two symbols on the right-hand side into binary form using intermediate
non-terminals,
- Replacing unit productions with their expansions or lexical mappings,
- Integrating the lexicon dictionary into the final CNF grammar.

Once the grammar is normalized, the `cky_parse` function performs bottom-up parsing on a tokenized
input sentence. It constructs a CKY parse table, indicating which non-terminals can derive which
subspans of the sentence. The parser determines whether the sentence can be derived from the start
symbol ("S") using the given grammar.

Overall, this project showcases foundational techniques in syntactic parsing and formal grammar
representation, integrating both theoretical and practical components of natural language syntax
as studied in the CMPE561 course.
"
"""

import pandas as pd

# Class to define context-free grammar (CFG) rules
class GrammarRule:
    def __init__(self, left, right):
        self.left = left  # Left-hand side non-terminal
        self.right = right  # Right-hand side as a list of terminals/non-terminals

    def __repr__(self):
        # Human-readable representation of the rule
        return f"{self.left} -> {' '.join(self.right)}"

# Class to define lexicon rules (mapping from POS tag to possible words)
class LexiconRule:
    def __init__(self, left, right):
        self.left = left  # POS tag
        self.right = right  # List of words that can take this POS tag

    def __repr__(self):
        # Human-readable representation of the lexicon rule
        return f"{self.left} -> {' | '.join(self.right)}"

    @staticmethod
    def from_lexicon_file(file_path):
        # Static method to read a lexicon table from an Excel file

        data = pd.read_excel(file_path)  # Read Excel file into a DataFrame

        lexicon_rules = []  # List to store lexicon rules

        for index, row in data.iterrows():
            tag = row['Tag']  # POS tag
            lexicon = row['lexicon']  # Associated words (comma-separated string)
            if pd.notna(lexicon):  # Check if lexicon cell is not NaN
                words = lexicon.split(',')  # Split comma-separated words
                lexicon_rules.append(LexiconRule(tag, [word.strip() for word in words]))  # Clean and add to rules

        return lexicon_rules  # Return list of LexiconRule objects

# List of CFG grammar rules, manually defined
cfg_grammarrules = [
    GrammarRule("S", ["NP", "VP"]),                        # S -> NP VP
    GrammarRule("S", ["VP"]),                              # S -> VP
    GrammarRule("S", ["V","NP","VP"]),                     # S -> Aux NP VP
    GrammarRule("S", ["Wh_NP","V","NP","VP"]),             # S -> Wh_NP Aux NP VP
    GrammarRule("NP", ["DT", "N"]),                        # NP -> Det N
    GrammarRule("NP", ["DT","AdjP", "N"]),                 # NP -> Det AdjP N
    GrammarRule("NP", ["AdjP", "NP"]),                     # NP -> AdjP NP
    GrammarRule("NP", ["AdjP", "N"]),                      # NP -> AdjP N
    GrammarRule("NP", ["NP", "CC","NP"]),                  # NP -> NP CC NP
    GrammarRule("NP", ["N"]),                              # NP -> N
    GrammarRule("N", ["PRP"]),                             # N -> PRP
    GrammarRule("N", ["NN"]),                              # N -> NN
    GrammarRule("N", ["NNmass"]),                          # N -> NNmass
    GrammarRule("N", ["NNS"]),                             # N -> NNS
    GrammarRule("VP", ["V", "NP","AdvP"]),                 # VP -> V NP AdvP
    GrammarRule("VP", ["V", "AdjP","PP"]),                 # VP -> V AdjP PP
    GrammarRule("VP", ["V", "NP","PP","AdvP"]),            # VP -> V NP PP AdvP
    GrammarRule("VP", ["V", "NP","PP","NP"]),              # VP -> V NP PP NP
    GrammarRule("VP", ["V"]),                              # VP -> V
    GrammarRule("VP", ["Aux", "NOT","VP"]),                # VP -> Aux NOT VP
    GrammarRule("VP", ["V", "TO","NP"]),                   # VP -> V TO NP
    GrammarRule("VP", ["V", "NP"]),                        # VP -> V NP
    GrammarRule("VP", ["V", "NP","PP"]),                   # VP -> V NP PP
    GrammarRule("VP", ["V", "AdvP"]),                      # VP -> V AdvP
    GrammarRule("VP", ["V", "PP"]),                        # VP -> V PP
    GrammarRule("V", ["Aux"]),                             # V -> Aux
    GrammarRule("V", ["Aux_past"]),                        # V -> Aux_past
    GrammarRule("V", ["VBD"]),                             # V -> VBD
    GrammarRule("V", ["VB"]),                              # V -> VB
    GrammarRule("V", ["VB_int"]),                          # V -> VB_int
    GrammarRule("PP", ["IN","NP"]),                        # PP -> IN NP
    GrammarRule("AdjP", ["JJ"]),                           # AdjP -> JJ
    GrammarRule("AdjP", ["AdvP","AdjP"]),                  # AdjP -> AdvP AdjP
    GrammarRule("AdvP", ["AdvP","RB"]),                    # AdvP -> AdvP RB
    GrammarRule("AdvP", ["RB"]),                           # AdvP -> RB
    GrammarRule("RB", ["RB_nonpast"]),                     # RB -> RB_nonpast
    GrammarRule("RB", ["RB_past"]),                        # RB -> RB_past
    GrammarRule("RB", ["RB_notime"]),                      # RB -> RB_notime
    GrammarRule("Wh_NP", ["WRB"]),                         # Wh_NP -> WRB
]

# Print all CFG grammar rules
for rule in cfg_grammarrules:
    print(rule)

# Define the path to the Excel file containing the lexicon table
file_path = '/content/lexicon table (1).xlsx'

# Generate lexicon rules from the Excel file
cfg_lexicon_rules = LexiconRule.from_lexicon_file(file_path)

# Print the lexicon rules
print("\nLexicon Rules:")
for rule in cfg_lexicon_rules:
    print(rule)

# Save the lexicon rules to a text file
output_file_path = 'cfg_lexicon_rules.txt'
with open(output_file_path, 'w') as file:
    file.write("\n".join(map(str, cfg_lexicon_rules)))  # Write each rule as a string, line by line

# Confirm successful file write
print(f"CFG rules saved to {output_file_path}")

# Function to load lexicon rules from a text file and store them in a dictionary
def load_lexicon_rules(file_path):

    lexicon_dict = {}  # Initialize an empty dictionary to store the rules

    # Open the file in read mode
    with open(file_path, 'r') as file:
        for line in file:
            # Strip newline characters and split the line into left and right parts of the rule
            left, right = line.strip().split(" -> ")

            # Split the right-hand side into individual word symbols using ' | ' as separator
            symbols = right.split(" | ")

            # Store the right-hand side list under the left-hand side key in the dictionary
            lexicon_dict[left] = symbols

    return lexicon_dict  # Return the complete dictionary of lexicon rules


# Specify the file path where the lexicon rules are stored
lexicon_file_path = 'cfg_lexicon_rules.txt'

# Load the rules into a dictionary using the defined function
lexicon_dict = load_lexicon_rules(lexicon_file_path)

# Class to convert a given CFG (with GrammarRules and Lexicon) into Chomsky Normal Form (CNF)
class CNFConverter:
    def __init__(self, grammar_rules, lexicon_dict):
        self.grammar_rules = grammar_rules         # List of GrammarRule objects
        self.new_rules = []                        # Store newly generated rules
        self.new_non_terminal_count = 0            # Counter for generating new non-terminal symbols
        self.lexicon_dict = lexicon_dict           # Dictionary mapping POS tags to terminal words

    def generate_new_non_terminal(self):
        # Generates a new non-terminal name like X1, X2, ...
        self.new_non_terminal_count += 1
        return f"X{self.new_non_terminal_count}"

    def break_rule(self, left, right):
        # Breaks a long rule (with RHS length > 2) into binary rules using new non-terminals
        intermediate_rules = []

        # Keep breaking until only 2 symbols remain on RHS
        while len(right) > 2:
            new_non_terminal = self.generate_new_non_terminal()
            # Create a new rule for the first two symbols
            intermediate_rules.append(GrammarRule(new_non_terminal, tuple(right[:2])))
            # Replace the first two symbols with the new non-terminal
            right = [new_non_terminal] + right[2:]

        # Add the final rule with only 2 symbols on RHS
        intermediate_rules.append(GrammarRule(left, tuple(right)))
        return intermediate_rules

    def convert_to_cnf(self):
        CNF_grammar_rules = []  # Will store final CNF rules
        intermediate_rules = []  # Store intermediate rules generated from long RHS

        # Iterate over original grammar rules
        for rule in self.grammar_rules:

            # Case 3: If RHS has more than 2 symbols, break it down
            if len(rule.right) > 2:
                new_rules = self.break_rule(rule.left, rule.right)
                CNF_grammar_rules.append((new_rules[-1].left, new_rules[-1].right))  # Add final binary rule
                intermediate_rules.extend([(r.left, r.right) for r in new_rules[:-1]])  # Collect intermediate rules

            # Case 2: Unit productions (e.g., A -> B)
            elif len(rule.right) == 1:
                rhs = rule.right[0]
                lhs = rule.left

                # If RHS refers to a lexicon category, replace it with the corresponding terminals
                if rhs in self.lexicon_dict:
                    CNF_grammar_rules.append((rule.left, self.lexicon_dict[rhs]))

                else:
                    # Otherwise, check for indirect mappings (e.g., A -> B and B -> ...)
                    for rule2 in self.grammar_rules:
                        rhs2 = rule2.right
                        lhs2 = rule2.left

                        if rhs == lhs2 and len(rhs2) > 2:
                            # Break long rules found in the referenced rule
                            new_rules = self.break_rule(rule2.left, rule2.right)
                            CNF_grammar_rules.append((lhs, new_rules[-1].right))
                            intermediate_rules.extend([(r.left, r.right) for r in new_rules[:-1]])

                        elif rhs == lhs2 and len(rhs2) == 2:
                            # Directly add binary rule if found
                            CNF_grammar_rules.append((lhs, rhs2))

                        elif rhs == lhs2 and len(rhs2) == 1:
                            # Resolve unit-to-lexicon if possible
                            if rhs2[0] in self.lexicon_dict:
                                CNF_grammar_rules.append((lhs, self.lexicon_dict[rhs2[0]]))

            # Case 1: Rule already in binary form (A -> B C)
            elif len(rule.right) == 2:
                CNF_grammar_rules.append((rule.left, tuple(rule.right)))

        # Finally, add all lexicon entries as terminal rules (e.g., NN -> "dog")
        for rule in self.lexicon_dict:
            lex_lhs = rule
            CNF_grammar_rules.append((lex_lhs, self.lexicon_dict[lex_lhs]))

        # Combine all CNF and intermediate rules into one final grammar
        grammar = CNF_grammar_rules + intermediate_rules

        return grammar


# Instantiate the CNFConverter with grammar rules and the lexicon dictionary
cnf_converter = CNFConverter(cfg_grammarrules, lexicon_dict)

# Perform the CNF conversion
cnf_rules = cnf_converter.convert_to_cnf()

# Output the resulting CNF rules
print("\nCNF Rules:")
for rule in cnf_rules:
    print(rule)

# CKY (Cocke-Kasami-Younger) parser implementation
# Takes a list of input words and a CNF grammar, returns a parse table
def cky_parse(words, grammar):

    n = len(words)  # Number of words in the input sentence

    # Initialize the CKY parse table as an n x (n+1) upper-triangular table of sets
    # Each cell table[i][j] stores the set of non-terminals that derive the span words[i:j]
    table = [[set() for _ in range(n + 1)] for _ in range(n)]

    # Fill in the diagonal of the table (single-word spans)
    for j in range(1, n + 1):
        for lhs, rhs in grammar:
            # Check if the current word matches a terminal rule
            if words[j - 1] in rhs:
                table[j - 1][j].add(lhs)  # Add the LHS non-terminal to the corresponding cell

    # Loop over increasing span lengths (2 to n)
    for span in range(2, n + 1):
        for i in range(n - span + 1):
            j = i + span
            for k in range(i + 1, j):
                # Try all binary grammar rules: A -> B C
                for lhs, rhs in grammar:
                    if isinstance(rhs, tuple) and len(rhs) == 2:
                        B, C = rhs
                        # If the left part (B) derives words[i:k] and right part (C) derives words[k:j]
                        if B in table[i][k] and C in table[k][j]:
                            table[i][j].add(lhs)  # Add the resulting non-terminal A to table[i][j]

    return table  # Return the filled CKY parse table


# Example input sentence
words = ["when", "did", "you", "come", "here", "lastly"]

# Run CKY parser on the sentence using the CNF grammar
parse_table = cky_parse(words, cnf_rules)

# Print each row of the parse table (for inspection)
for row in parse_table:
    print(row)

words = ["I", "enjoy", "historical", "novels"]


parse_table = cky_parse(words, cnf_rules)

for row in parse_table:
    print(row)

words = ["do", "not", "listen", "to","loud","music"]


parse_table = cky_parse(words, cnf_rules)

for row in parse_table:
    print(row)

words = ["I", "helped", "my", "mother","with","dinner","yesterday"]


parse_table = cky_parse(words, cnf_rules)

for row in parse_table:
    print(row)

words = ["will", "you", "attend", "the","meeting","tonight"]


parse_table = cky_parse(words, cnf_rules)

for row in parse_table:
    print(row)

words = ["watermelon", "is", "the", "most","beautiful","fruit","of","summer"]


parse_table = cky_parse(words, cnf_rules)

for row in parse_table:
    print(row)