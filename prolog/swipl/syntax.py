from re import compile

SWI_PROMPT = "[?][-][ ]"
SWI_ERROR = "ERROR.*"
SWI_MULTIPLE = r"\w+ = .*? $"

VAR = compile(r"[^a-zA-Z0-9_]([A-Z][a-zA-Z0-9_]*)")
RES = compile(r"L = (\[.*\])[., ]")
MULTI_RES = compile(r"(\w+) = (.*?)(?:,\r\n| $|\.\r\n\r\n\?- $| .*\.)")
