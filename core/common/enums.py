from enum import Enum

class GeneralError(Enum):
    UnexpectedOntology = 'Unexpected ontology'
    BadFormatting = 'Bad formatting'

class CommandResult(Enum):
    Success = 'Success'
    AlreadyInPosition = 'Switch already in position'
    NotFound = 'Switch not found'
    Unknown = 'Unknown error'


class SwitchAlreadyInPosition(Exception):
    pass