.. _`basic tutorial`:

Basic tutorial
==============

In this tutorial we will build a simple robot language to demonstrate
the basic workflow when working with textX.


Robot language
--------------

When building a DSL we should first do a domain analysis, to see what concepts
do we have and what are their relationships and constraints. In the following
paragraph a short analysis is done. Important concepts are emphasized.

In this case we want an imperative language that should define robot movement on
the imaginary grid.  Robot should **move** in four base **direction**. We will
call that direction **up, down, left** and **right** (you could use north,
south, west and east if you like).  Additionally, we shall have a robot
coordinate given in x, y **position**.  For simplicity our robot can move in
discrete **steps**. In each movement robot can move by 1 or more steps but in
the same direction. Coordinate is given as a pair of integer numbers. Robot will
have an **initial position**. If not given explicitly it is assumed that
position is (0, 0).


So, lets build a simple robot language.


Grammar
-------

First we need to define a grammar for the language. In textX the grammar will
also define a meta-model (a.k.a. abstract syntax) for the language which can be
visualized and be used as a part of the documentation.

Usually we start by outlining some program in the language we are building.

Here is an example of *program* on robot language::

   begin
       initial 3, 1
       up 4
       left 9
       down
       right 1
   end

We have :code:`begin` and :code:`end` keywords that define the beginning and
end of the program. In this case we could do without these keywords but lets
have it to make it more interesting.

In between those two keywords we have a sequence of instruction. First
instruction will position our robot at coordinate (3, 1). After that robot will
move up 4 steps, left 9 steps, down 1 step (1 step is default) and finally 1
step to the right.

Lets start with grammar definition. We shall start in a top-down manner so lets
first define a program as a whole::

  Program:
    'begin'
      commands*=Command
    'end'
  ;


Here we see that our program is defined with sequence of:

* string match (:code:`'begin'`),
* zero or more assignment to :code:`commands` attribute,
* string match (:code:`'end'`).

String matches will require literal strings given at the begin and end of
program. If this is not satisfied a syntax error will be raised. This whole rule
(Program) will create a class with the same name in the meta-model. Each program
will be an instance of this class. :code:`commands` assignment will result in a
python attribute :code:`commands` on the instance of :code:`Program` class. This
attribute will be of :code:`list` type (because :code:`*=` assignment is used).
Each element of this list will be a specific command.

Now, we see that we have different types of commands. First command has two
parameters and it defines the robot initial position. Other commands has one or
zero parameters and define the robot movement.

To state that some textX rule is specialised in 2 or more rules we use an
abstract rule. For :code:`Command` we shall define two specializations:
:code:`InitialCommand` and :code:`MoveCommand` like this::

  Command:
    InitialCommand | MoveCommand
  ;

Abstract rule is given as ordered choice of other rules.
This can be read as "Each command is either a InitialCommand or
MoveCommand".


Lets now define command for setting initial position::

  InitialCommand:
    'initial' x=INT ',' y=INT
  ;

This rule specifies a class :code:`InitialCommand` in the meta-model. Each initial
position command will be an instance of this class.

So, this command should start with keyword :code:`initial` after which we give
an integer number (base type rule INT - this number will be available as
attribute :code:`x` on the :code:`InitialCommand` instance), than a separator
:code:`,` is required after which we have y coordinate as integer number (this
will be available as attribute :code:`y`). Using base type rule INT matched
number from input string will be automatically converted to python type
:code:`int`.

Now, lets define a movement command. We know that this command consists of
direction identifier and optional number of steps (if not given the default will
be 1)::

  MoveCommand:
    direction=Direction (steps=INT)?
  ;

So, the movement command model object will have two attributes.
:code:`direction` attribute will define one of the four possible directions and
:code:`steps` attribute will be an integer that will hold how many steps a robot
will move in given direction. Steps are optional so if not given in the program
it will still be a correct syntax. Notice, that the default of 1 is not
specified in the grammar. The grammar deals with syntax constraints. Additional
semantics will be handled later in model/object processors (see below).

Now, the missing part is :code:`Direction` rule referenced from the previous
rule. This rule will define what can be written as a direction.
We will define this rule like this::

  Direction:
    "up"|"down"|"left"|"right"
  ;

This kind of rule is called a *match rule*. This rule does not result in a new
object. It consists of ordered choice of simple matches (string, regex), base
type rules (INT, STRING, BOOL...) and/or other match rule references.

The result of this match will be assigned to the attribute from which it was
referenced. If base type was used it will be converted in a proper python type.
If not, it will be a python string that will contain the text that was matched
from the input.

In this case a one of 4 words will be matched and that string will be assigned
to the :code:`direction` attribute of the :code:`MoveCommand` instance.

The final touch to the grammar is a definition of comment rule. We want to comment
our robot code, right?

In textX a special rule called :code:`Comment` is used for that purpose.
Lets define a C-style single line comments::

  Comment:
    /\/\/.*$/
  ;


Our grammar is done. Save it in :code:`robot.tx` file. The content of this file
should now be::


  Program:
    'begin'
      commands*=Command
    'end'
  ;

  Command:
    InitialCommand | MoveCommand
  ;

  InitialCommand:
    'initial' x=INT ',' y=INT
  ;

  MoveCommand:
    direction=Direction (steps=INT)?
  ;

  Direction:
    "up"|"down"|"left"|"right"
  ;

  Comment:
    /\/\/.*$/
  ;


Notice that we have not constrained initial position command to be specified
just once on the beginning of the program. This basically means that this
command can be given multiple times throughout the program. I will leave as an
exercise to the reader to implement this constraint.

Instantiating meta-model
------------------------

In order to parse our models we first need to construct a meta-model. A
textX meta-model is a Python object that contains all classes that can be
instantiated in our model. For each grammar rule a class is created.
Additionally, meta-model contains a parser that knows how to parse input
strings. From parsed input (parse tree) meta-model will create a model.

Meta-models are created from our grammar description, in this case
:code:`robot.tx` file::

  from textx.metamodel import metamodel_from_file
  robot_mm = metamodel_from_file('robot.tx')

Next step during language design is meta-model visualization. It is usually
easier to comprehend our language if rendered graphically. To do so we use
excellent `GraphViz`_ software package and its DSL for graph specification
called *dot*. It is a textual language for visual graph definition.

Lets export our meta-model to dot language::

  from textx.export import metamodel_export
  metamodel_export(robot_mm, 'robot_meta.dot')

First parameter is our meta-model object while the second is an output dot
filename.

:code:`dot` file can be opened with dot viewer (there are many to choose
from) or transformed with :code:`dot` tool to raster or vector graphics.

For example::

  dot -Tpng robot_meta.dot -O robot_meta.png

This command will create :code:`png` image out of :code:`dot` file.

|robot_meta.dot|


.. _GraphViz:: http://www.graphviz.org/
.. |robot_meta.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/robot/robot_meta.dot.png

.. note::

   This meta-model can be used to parse multiple models.

Instantiating model
-------------------

Now, when we have our meta-model we can parse models from strings or external
textual files::

  robot_model = robot_mm.model_from_file('program.rbt')

This command will parse file :code:`program.rbt` and constructs our robot model.
In this file does not match our language a syntax error will be raised on the
first error encountered.

In the same manner as meta-model visualization we can visualize our model too::

  from textx.export import model_export
  model_export(robot_model, 'program.dot')

This will create :code:`program.dot` file that can be visualized using proper
viewer or transformed to image::

  dot -Tpng program.dot -O program.png

For the robot program above we should get an image like this:

|program.dot|

.. |program.dot| image:: https://raw.githubusercontent.com/igordejanovic/textX/master/examples/robot/program.dot.png

Interpreting model
------------------

When we have successfully parsed and loaded our model/program (or mogram or
prodel ;) ) we can do various stuff. Usually what would you like to do is to
translate your program to some other language (Java, Python, C#, Ruby,...) or
you could build an interpreter that will evaluate/interpret your model directly.
Or you could analyse your model, extract informations from it etc. It is up to
you to decide.

We will show here how to build a simple interpreter that will start the robot
from the initial position and print the position of the robot after each
command.

Lets imagine that we have a robot that understands our language::

  class Robot(object):

    def __init__(self):
      # Initial position is (0,0)
      self.x = 0
      self.y = 0

    def __str__(self):
      return "Robot position is {}, {}.".format(self.x, self.y)

Now, our robot will have an :code:`interpret` method that accepts our robot
model and runs it. At each step this method will update the robot position and
print it::

  def interpret(self, model):

      # model is an instance of Program
      for c in model.commands:

          if c.__class__.__name__ == "InitialCommand":
              print("Setting position to: {}, {}".format(c.x, c.y))
              self.x = c.x
              self.y = c.y
          else:
              dir = c.direction
              print("Going {} for {} step(s).".format(dir, c.steps))

              move = {
                  "up": (0, 1),
                  "down": (0, -1),
                  "left": (-1, 0),
                  "right": (1, 0)
              }[dir]

              # Calculate new robot position
              self.x += c.steps * move[0]
              self.y += c.steps * move[1]

          print(self)

Now lets give our :code:`robot_model` to :code:`Robot` instance and see what
happens::

  robot = Robot()
  robot.interpret(robot_model)

You should get this output::

  Setting position to: 3, 1
  Robot position is 3, 1.
  Going up for 4 step(s).
  Robot position is 3, 5.
  Going left for 9 step(s).
  Robot position is -6, 5.
  Going down for 0 step(s).
  Robot position is -6, 5.
  Going right for 1 step(s).
  Robot position is -5, 5.

It is *almost* correct. We can see that down movement is for 0 steps because we
have not defined the steps for :code:`down` command and haven't done anything
yet to implement default of 1.

The best way to implement default value for step is to use so called *object
processor* for :code:`MoveCommand`.
Object processor is a callable that gets called whenever textX parses and
instantiates an object of particular class. You can register object processors
for the classes your wish to process in some way immediately after
instantiation.

Lets define our processor for :code:`MoveCommand`::

  def move_command_processor(move_cmd):

    if move_cmd.steps == 0:
      move_cmd.steps = 1


Now, register this processor on meta-model. After meta-model construction add a
line for registration::

  robot_mm.register_obj_processors({'MoveCommand': move_command_processor})

:code:`register_obj_processors` accepts a dictionary keyed by class name. The
values are callables that should handle instances of the given class.

If you run robot interpreter again you will get output like this::

  Setting position to: 3, 1
  Robot position is 3, 1.
  Going up for 4 step(s).
  Robot position is 3, 5.
  Going left for 9 step(s).
  Robot position is -6, 5.
  Going down for 1 step(s).
  Robot position is -6, 4.
  Going right for 1 step(s).
  Robot position is -5, 4.

And now our robot behaves as expected!

.. note::

  The code from this tutorial can be found in the *examples/robot* folder.

