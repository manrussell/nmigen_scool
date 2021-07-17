# based on video from  Robert Baruch
# https://www.youtube.com/watch?v=AQOXoKQhG3I&t=2613s

from typing import List

from nmigen import *
from nmigen.build import Platform
from nmigen.cli import main_parser
from nmigen.sim import Simulator, Delay
from nmigen.asserts import Assert

class Clocky(Elaboratable):
    def __init__(self):
        # 8 wires, default unsigned
        self.x      = Signal(8)
        self.load   = Signal(8)
        self.value  = Signal(8)

    # python type annotation .. -> Module:
    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # there is always a clock called sync
        # on the rising edge of a clock pulse...
        #   Mux is equivalent to the ternary operator in C
        with m.If(self.load):
            m.d.sync += self.x.eq(Mux(self.value <= 100, self.value, 100))
        with m.If(self.x == 100):
            m.d.sync += self.x.eq(0)
        with m.Else():
            m.d.sync += self.x.eq(self.x + 1)

        return m

    # return a list of public signals
    def ports(self) -> List[Signal]:
        return[self.x, self.load, self.value]


if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    # define top level module
    m = Module()
    m.submodules.clocky = clocky = Clocky()

    # Use Assert() with main_runner() do not simulate i believe ??

    # Past(clocky.x) is last value of clocky.x one clock cycle earlier
    # with m.If((clocky.x > 0) & (Past(clocky.load) == 0)):
    #     m.d.sync += Assert(clocky.x == (Past(clocky.x) + 1)[:8])

    # main_runner(parser, args, m, ports=[] + clocky.ports())

    load = Signal()
    value = Signal(8)
    m.d.comb += clocky.load.eq(load)
    m.d.comb += clocky.value.eq(value)

    sim = Simulator(m)
    # specify a clock with period 1us
    sim.add_clock(1e-6)

    #
    def process():
        # wait one clock process, 50% duty
        yield
        # set load ...
        yield load.eq(1)
        # and set value ...
        yield value.eq(95)
        # and wait one clock period, 
        # the value of .eq(95) will occur just after the clock edge
        yield
        yield
        yield value.eq(0)
        yield
        yield
        yield
        yield
        yield

    # add sync process not combinatorial processes
    sim.add_sync_process(process)
    with sim.write_vcd("clockyTest.vcd", "clockyTest.gtkw", traces=[] + clocky.ports()):
        sim.run()
