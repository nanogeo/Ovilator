
from enum import Enum


class EnemyPlan:
    MACRO = 1
    TURTLE = 2
    TECHING = 3
    TIMING_ATTACK = 4
    ALL_IN = 5
    CHEESE = 6

class ArmyComp:
    LING_BANE_HYDRA = 1
    ROACH_HYDRA = 2
    LING_BANE_MUTA = 3
    ROACH_SWARM_HOST = 4

class ArmyState:
    CONSOLIDATING = 1
    RALLYING = 2
    ATTACKING = 3
    PROTECTING = 4

class EnemyArmyState:
    DEFENDING = 1
    PREPARING_ATTACK = 2
    MOVING_TO_ATTACK = 3
    
class MutaGroupState:
    CONSOLIDATING = 1
    MOVING_TO_RALLY = 2
    MOVING_TO_ATTACK = 3
    ATTACKING = 4
    RETREATING = 5
    
class SwarmHostState:
    WAITING = 1
    UNLOADING = 2

class QueenState:
    SPREAD_CREEP = 1
    DEFEND = 2
    SPREAD_CAREFULLY = 3
    
class LingRunby:
    ling_tags = []
    path = []
    target = None
    
class ProxyStatus(Enum):
    NONE = 1
    PR_RAX_STARTED = 10
    PR_SOME_RAX_FINISHED = 11
    PR_ALL_RAX_FINISHED = 12
    PR_UNPROTECTED_BUNKER = 13
    PR_PROTECTED_BUNKER = 14
    PR_NO_BUNKER_ATTACK = 15
    PR_BUNKER_FINISHED = 16
    
class MinerStatus(Enum):
    MOVING_TO_HATCH = 1
    MOVING_TO_MINERALS = 2
    MINING = 3
