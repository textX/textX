from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export

robot_mm = metamodel_from_file('robot.tx', debug=True)
metamodel_export(robot_mm, 'robot_meta.dot')

robot_model = robot_mm.model_from_file('program.rbt')
model_export(robot_model, 'program.dot')

