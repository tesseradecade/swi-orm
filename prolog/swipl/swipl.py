import pexpect as px
import typing

from .syntax import SWI_PROMPT, SWI_ERROR, VAR, RES
from prolog.swipl.exception import (
    SWIExecutableNotFound,
    SWICompileError,
    SWIQueryError,
    SWIQueryTimeout,
)


def default_parser(value: str, lvars: typing.List[str]) -> list:
    return value.strip("[]").split(", ")


class Swipl:
    """Python interface to SWI Prolog (http://www.swi-prolog.org)"""

    def __init__(
        self, path_to_swipl: str = "/path/to/swipl", args: typing.List[str] = None
    ):
        """Constructor method
        Usage: swipl( path, args )
        path - path to SWI executable (default: 'swipl')
        args - command line arguments (default: '-q +tty')
        self.engine becomes pexpect spawn instance of SWI Prolog shell
        Raises: SWIExecutableNotFound"""
        if args is None:
            args = ["-q", "+tty"]

        self.parser: typing.Callable[[str, typing.List[str]], list] = default_parser

        try:
            self.engine = px.spawn(path_to_swipl + " " + " ".join(args))
            self.engine.expect(SWI_PROMPT, timeout=3)
        except px.ExceptionPexpect:
            raise SWIExecutableNotFound(
                "SWI-Prolog executable not found on the specified path. "
                f'Try installing swi-prolog or using swipl( "{path_to_swipl}" )'
            )

    def load(self, path: str) -> None:
        """Loads module into self.engine
        Usage: instance.load( path )
        module - path to module file
        Raises: SWICompileError"""
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
        """Simply loads line for base swi compiler"""
        for line in lines:
            if line.endswith("."):
                line = line[:-1]
            self.engine.sendline(f"assert(({line})).")
            self.engine.readline()

            index = self.engine.expect([SWI_ERROR, SWI_PROMPT], timeout=3)
            if not index:
                raise SWICompileError(
                    'Error while compiling line "'
                    + line
                    + '". Error from SWI:\n'
                    + str(self.engine.after)
                )

    def query(self, query: str) -> typing.Union[bool, list]:
        """Queries current engine state
        Usage: instance.query( query )
        query - usual SWI Prolog query (example: 'likes( X, Y )')
        Returns:
          True - if yes/no query and answer is yes
          False - if yes/no query and answer is no
          List of dictionaries - if normal query. Dictionary keys are returned
          variable names.
        Raises: SWIQueryError"""
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
                    + str(self.engine.after)
                )
            return "true" in str(self.engine.after)
        else:
            printer = self._printer(lvars, query)
            self.engine.sendline(printer)
            self.engine.readline()
            index = self.engine.expect([SWI_ERROR, SWI_PROMPT], timeout=3)
            if not index:
                raise SWIQueryError(
                    'Error while executing query "'
                    + query
                    + '". Error from SWI:\n'
                    + str(self.engine.after)
                )
            state = str(self.engine.before)
            state = state.replace("\\r", "").replace("\\n", "")
            res = RES.search(str(state))
            results = self.parser(res.groups()[0], lvars)
            if not results:
                return False
            return results

    @property
    def response_parser(self) -> typing.Callable[[str, typing.List[str]], list]:
        return self.parser

    @response_parser.setter
    def response_parser(
        self, new_response_parser: typing.Callable[[str, typing.List[str]], list]
    ):
        self.parser = new_response_parser

    @staticmethod
    def _printer(lvars: typing.List[str], query: typing.List[str]) -> str:
        """Private method for constructing a result printing query.
        Usage: instance._printer( lvars, query )
        lvars - list of logical variables to print
        query - query containing the variables to be printed
        Returns: string of the form 'query, writeln( res( 'VarName1', VarName1 ) ) ... writeln( res( 'VarNameN', VarNameN ) ),nl,fail.'
        """
        query = query[:-1]
        if len(lvars) > 1:
            lvars = ",".join(lvars)
            return f"bagof([{lvars}], {query}, L)."
        return f"bagof({lvars[0]}, {query}, L)."
