from re import compile

SWI_PROMPT = "[?][-][ ]"
SWI_ERROR = "ERROR.*"

VAR = compile(r"[^a-zA-Z0-9_]([A-Z][a-zA-Z0-9_]*)")
RES = compile(r"L = (\[.*\])\.")
