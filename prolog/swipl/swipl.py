import pexpect as px
import typing
import re
import choicelib

from .syntax import SWI_PROMPT, SWI_ERROR, VAR, RES, SWI_MULTIPLE, MULTI_RES
from prolog.swipl.exception import (
    SWIExecutableNotFound,
    SWICompileError,
    SWIQueryError,
    SWIQueryTimeout,
)


json = choicelib.choice_in_order(
    ["json", "ujson", "hyperjson", "orjson"], do_import=True
)
QueryResponse = typing.Union[dict, bool]


class Swipl:
    """ Python interface to SWI Prolog (http://www.swi-prolog.org) """

    def __init__(
        self, path_to_swipl: str = "/path/to/swipl", args: typing.List[str] = None
    ):
        """ Constructor method
        Usage: swipl( path, args )
        path - path to SWI executable (default: 'swipl')
        args - command line arguments (default: '-q +tty')
        self.engine becomes pexpect spawn instance of SWI Prolog shell
        Raises: SWIExecutableNotFound """
        if args is None:
            args = ["-q", "+tty"]

        try:
            self.engine = px.spawn(path_to_swipl + " " + " ".join(args))
            self.engine.expect(SWI_PROMPT, timeout=3)
        except px.ExceptionPexpect:
            raise SWIExecutableNotFound(
                "SWI-Prolog executable not found on the specified path. "
                f'Try installing swi-prolog or using swipl( "{path_to_swipl}" )'
            )

    def load(self, path: str) -> None:
        """ Loads module into self.engine
        Usage: instance.load( path )
        module - path to module file
        Raises: SWICompileError """
        self.engine.sendline("['" + path + "'].")
        self.engine.readline()
        index = self.engine.expect([SWI_ERROR, SWI_PROMPT], timeout=3)
        if not index:
            raise SWICompileError(
                'Error while compiling module "'
                + path
                + '". Error from SWI:\n'
                + str(self.engine.after)
            )

    def load_lines(self, lines: typing.List[str]):
        """ Simply loads line for base swi compiler """
        for line in lines:
            if line.endswith("."):
                line = line[:-1]

            self.engine.sendline(f"assert(({line})).")
            self.engine.readline()

            index = self.engine.expect([SWI_ERROR, "true.*?[?][-][ ]"], timeout=3)

            if not index:
                raise SWICompileError(
                    'Error while compiling line "'
                    + line
                    + '". Error from SWI:\n'
                    + self.engine.after.decode()
                )

    def query(self, query: str) -> typing.Iterator[QueryResponse]:
        """ Queries current engine state """
        query = query.strip()

        if not query.endswith("."):
            query += "."

        lvars = VAR.findall(query)
        lvars = list(set(lvars))

        if not lvars:
            self.engine.sendline(query)
            self.engine.readline()
            try:
                index = self.engine.expect(
                    [".*true.*", SWI_ERROR, ".*false.*", SWI_PROMPT], timeout=5
                )
            except SWIQueryTimeout:
                raise SWIQueryTimeout("Timeout exceeded")

            if index == 1:
                raise SWIQueryError(
                    'Error while executing query "'
                    + query
                    + '". Error from SWI:\n'
                    + self.engine.after.decode()
                )
            yield "true" in str(self.engine.after)
        else:
            self.engine.sendline(query)
            self.engine.readline()

            index = self.engine.expect([SWI_ERROR, SWI_MULTIPLE], timeout=3)
            # print(self.engine.before)

            if index == 0:
                raise SWIQueryError(
                    'Error while executing query "'
                    + query
                    + '". Error from SWI:\n'
                    + self.engine.after.decode()
                )

            elif index == 1:
                yield self.process_multi_res(self.engine.after)

                while index == 1:
                    self.engine.send(";")
                    # self.engine.readline()

                    index = self.engine.expect([SWI_ERROR, SWI_MULTIPLE], timeout=3)
                    # print(self.engine.before.decode())

                    yield self.process_multi_res(self.engine.after)

                    if self.engine.after.endswith(b"?- "):
                        break

    def halt(self):
        self.engine.sendline("halt(0).")

    def send_dot(self):
        self.engine.send(".")

    @staticmethod
    def process_data(before: bytes) -> typing.Any:
        state = str(before)
        state = state.replace("\\r", "").replace("\\n", "")
        res = RES.search(str(state))
        return res

    @staticmethod
    def process_multi_res(b: bytes) -> dict:
        multi_res = re.findall(MULTI_RES, b.decode())
        return json.loads(
            "{" + ", ".join(f'"{k.lower()}": {v}' for (k, v) in multi_res) + "}"
        )
