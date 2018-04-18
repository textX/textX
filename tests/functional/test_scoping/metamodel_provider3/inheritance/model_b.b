B:
import "model_a.a"

class B1 extends A1 {
  method b1
}
class B2 extends A2 {
  method b2
  method b2_very_long_name
}
class B3 extends A3 {
  method b3
}
class B4 extends A4 {
  method b4
}
class B5 extends B4 {
  method b5
}
class B6 extends B5 {
  method b6
}

