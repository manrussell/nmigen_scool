# based on video from  Robert Baruch
# https://www.youtube.com/watch?v=AQOXoKQhG3I&t=2613s

from typing import List

from nmigen import *
from nmigen.build import Platform
from nmigen.cli import main_parser
from nmigen.sim import Simulator, Delay

class Adder(Elaboratable):
    def __init__(self):
        # 8 wires, default unsigned
        self.x = Signal(8)
        self.y = Signal(8)
        self.out = Signal(8)


    # python type annotation .. -> Module:
    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # generates code for "add x + y"
        m.d.comb += self.out.eq(self.x + self.y)

        return m


    # return a list of public signals
    def ports(self) -> List[Signal]:
        return[self.x, self.y, self.out]


if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    # define top level module
    m = Module()

    # add sub-modules to it and give it a name, so it will display in gtkwave
    m.submodules.adder = adder = Adder()
    # this version does not give it a name
    # m.submodules.adder += Adder()


    #
    # for simulator remove the main_runner() as we are not outputting to ..
    #
    # put args into parser, add module, add ports we are interested in outputting to a trace if doing simulation or yo-sis if doing formal verification
    # main_runner(parser, args, m, ports=[] + adder.ports())

    #
    #
    # for simulating
    #

    # these lines are important because they are our input lines and if we want to trace them 
    # we need to init them here
    x = Signal(8)
    y = Signal(8)

    m.d.comb += adder.x.eq(x)
    m.d.comb += adder.y.eq(y)

    sim = Simulator(m)

    # a generator, so requires a yield
    def count_process():
        yield x.eq(0x00)
        yield y.eq(0x00)
        # no clock here so use a Delay()
        yield Delay(1e-6)
        yield x.eq(0xFF)
        yield y.eq(0xFF)
        yield Delay(1e-6)
        yield x.eq(0x05)
        yield y.eq(0x50)
        yield Delay(1e-6)

    sim.add_process(count_process)
    # creates files which you open with gtkwave countTest.vcd 
    with sim.write_vcd("adderTest.vcd", "adderTest.gtkw", traces=[x, y] + adder.ports()):
        sim.run()
