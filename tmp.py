from textx import metamodel_from_str
from textx.scoping.providers import RelativeName, FQN
from textx.export import model_export
# ------------------------------------
# GRAMMAR
#
meta_model = metamodel_from_str('''
    Model: aspects+=Aspect scenarios+=Scenario testcases+=Testcase;
    Scenario: 'SCENARIO' name=ID 'BEGIN' 
        configs+=Config
    'END';
    Config: 'CONFIG' name=ID 'HAS' '(' haves*=[Aspect] ')';
    Aspect: 'ASPECT' name=ID;
    Testcase: 'TESTCASE' name=ID 'BEGIN'
        'USES' scenario=[Scenario] 'WITH' config=[Config]
        'NEEDS' '(' needs*=[Aspect] ')'
    'END';
    Comment: /\/\/.*/;
''')

# ------------------------------------
# SCOPING
#
meta_model.register_scope_providers({
    '*.*': FQN(),
    'Testcase.config': RelativeName('scenario.configs')
})

# ------------------------------------
# VALIDATION
#
def check_testcase(testcase):
    """
    checks that the config used by the test case fullfils its needs
    """
    for need in testcase.needs:
        if need not in testcase.config.haves:
            raise Exception("{}: {} not found in {}.{}".format(
                    testcase.name,
                    need.name,
                    testcase.scenario.name,
                    testcase.config.name
                    ))

meta_model.register_obj_processors({
        'Testcase': check_testcase
})

# ------------------------------------
# EXAMPLE
#
model = meta_model.model_from_str('''
    ASPECT Rain
    ASPECT Wind
    SCENARIO S001 BEGIN
        CONFIG HeavyRain HAS (Rain)
        CONFIG NoRain HAS ()
    END
    SCENARIO S002 BEGIN
        CONFIG WithWind HAS (Rain Wind)
        CONFIG NoWind HAS (Rain)
    END
    TESTCASE T001 BEGIN
        USES S001 WITH HeavyRain
        NEEDS (Rain)
    END
    TESTCASE T002 BEGIN
        //USES S001 WITH NoRain // Error
        USES S002 WITH NoWind
        NEEDS (Rain)
    END
''')

model_export(model, 'model.dot')