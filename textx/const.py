# Multiplicities
MULT_ONE = "1"
MULT_OPTIONAL = "0..1"
MULT_ZEROORMORE = "0..*"
MULT_ONEORMORE = "1..*"


priority = [MULT_OPTIONAL, MULT_ONE, MULT_ZEROORMORE, MULT_ONEORMORE]


def mult_lt(left, right):
    """
    Return True if left multiplicity is 'less than' right.
    """
    return priority.index(left) < priority.index(right)


# Rule types
# Common rules are rules that have direct or indirect assignments.
RULE_COMMON = "common"
# If the rule is ordered choice of other rules where there *MUST BE*
# assignments down the reference tree that this rule is abstract.
RULE_ABSTRACT = "abstract"
# If there is no direct or indirect assignments the rule is match rule.
RULE_MATCH = "match"


# TextXSemanticError types
MULT_ASSIGN_ERROR = "Multiple assignments"
UNKNOWN_OBJ_ERROR = "Unknown object"
