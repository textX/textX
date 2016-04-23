# Multiplicities
MULT_ONE = '1'
MULT_OPTIONAL = '0..1'
MULT_ZEROORMORE = '0..*'
MULT_ONEORMORE = '1..*'

# Rule types
# Common rules are rules that have direct or indirect assignments.
RULE_COMMON = "common"
# If the rule is ordered choice of other rules where there *MUST BE* assignments
# down the reference tree that this rule is abstract.
RULE_ABSTRACT = "abstract"
# If there is no direct or indirect assignments the rule is match rule.
RULE_MATCH = "match"
