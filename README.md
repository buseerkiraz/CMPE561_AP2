# CKY-Based Syntactic Parser for Turkish (CFG + CNF)

This project is developed for the **CMPE561 (Natural Language Processing)** Master's course at **Boğaziçi University**.  
It implements a **Context-Free Grammar (CFG)** based syntactic parser using the **CKY (Cocke-Kasami-Younger)** parsing algorithm. The full pipeline supports lexicon integration, grammar normalization into **Chomsky Normal Form (CNF)**, and parse table construction for input sentences.

---

## 📚 Overview

The system demonstrates a rule-based syntactic parsing approach in Turkish by combining:

- CFG grammar rule definition and lexical integration
- Conversion of grammar to CNF format for CKY compatibility
- A bottom-up CKY parsing algorithm to determine grammatical derivability

---

## 🔧 Components

### 1. Grammar Rules
- Defined using the `GrammarRule` class.
- Each rule follows the CFG format: `NonTerminal -> RHS1 RHS2 ... RHSN`.

### 2. Lexicon Integration
- Lexical rules (e.g., `NN -> kitap`, `VB -> okuyor`) are loaded from an Excel file via the `LexiconRule` class.
- The lexicon is stored as a dictionary mapping **POS tags** to their corresponding **word lists**.
- These allow linking terminal symbols (words) to non-terminal categories in the grammar.

### 3. CNF Conversion
- The `CNFConverter` class transforms the grammar into **Chomsky Normal Form** for CKY compatibility:
  - Rules with more than two RHS symbols are broken into binary productions using intermediate non-terminals.
  - Unit productions are replaced with their lexical or rule-based expansions.
  - Lexicon entries are integrated as terminal productions.

### 4. CKY Parsing
- The `cky_parse` function performs **bottom-up parsing** on a tokenized input sentence.
- It builds a 2D CKY parse table, indicating which non-terminals can generate each subspan of the input.
- The final goal is to check whether the **start symbol (`S`)** can derive the entire input sentence.

---

## Features

- Full CFG parser with CNF conversion support
- External lexicon loading from Excel files
- Modular classes for grammar rules, CNF conversion, and parsing
- Supports analysis of Turkish sentence structures

---

## 📌 Usage

```python
from parser import GrammarRule, LexiconRule, CNFConverter, cky_parse

# Load grammar and lexicon
grammar_rules = GrammarRule.load_from_file("grammar.txt")
lexicon = LexiconRule.load_from_excel("lexicon.xlsx")

# Convert to CNF
cnf_converter = CNFConverter(grammar_rules, lexicon)
cnf_rules = cnf_converter.convert()

# Parse a tokenized sentence
sentence = ["Ali", "kitap", "okuyor"]
cky_table = cky_parse(sentence, cnf_rules)

# Check if 'S' is in the top-right cell
if "S" in cky_table[0][-1]:
    print("Sentence is grammatically valid.")
else:
    print("Sentence is not derivable from the grammar.")
