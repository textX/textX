This is a simple Robot language.

The idea for this language came from [LISA robot
tutorial](http://labraj.feri.um.si/lisa/tutorial-robot.html).

For a full explanation see [the
tutorial](https://textx.github.io/textX/stable/tutorials/robot/).

To run the example do the following:

- Verify that textX is installed. See documentation how to do that.
- From the robot example folder run

        $ python robot.py

  You should get following output:

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

- Previous command will generate dot files for robot language meta-model and
  example robot program. To convert those files to PNG format do (you must have
  [GraphViz](http://graphviz.org/) installed):

        $ dot -Tpng -O *.dot

  You will get `robot_meta.dot.png` (robot meta-model) and `program.dot.png`
  (example robot program/model) diagram.

