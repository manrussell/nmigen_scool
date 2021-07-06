# based on video from  Robert Baruch
# https://www.youtube.com/watch?v=AQOXoKQhG3I&t=2613s

# GENERAL DESCRIPTION: The AD7302 is a dual, 8-bit voltage out DAC that operates 
# from a single +2.7 V to +5.5 V supply. Its on-chip precisionoutput buffers 
# allow the DAC outputs to swing rail to rail. TheAD7302 has a parallel 
# microprocessor and DSP-compatibleinterface with high speed registers and 
# double buffered interfacelogic.

from typing import List

from nmigen import *
from nmigen.build import Platform
from nmigen.cli import main_parser
from nmigen.sim import Simulator, Delay

class AD7302(Elaboratable):
    def __init__(self):
        # ins from Ym2151
        # 01(clock for D/A), 
        # SO, Data serial out
        # SH2, sample and hold
        # SH1, 
        # IC(initial clear)
        # VDD, 
        # VSS, Data ground

        self.si = Signal(8)
        # self.clk = Signal(8)
        # self. = Signal(8)




        # outs/inputs to AD7302 DAC
        # Parallel Data Inputs. Eight-bit data is loaded to the input register 
        # of the AD7302 under the control of CS and WR
        self.outDB0 = Signal(1)
        self.outDB1 = Signal(1)
        self.outDB2 = Signal(1)
        self.outDB3 = Signal(1)
        self.outDB4 = Signal(1)
        self.outDB5 = Signal(1)
        self.outDB6 = Signal(1)
        self.outDB7 = Signal(1)
        
        # control logic
        # Data is loaded to the registers on the rising edge of CS(active high)
        # or WR(active high) and the A/B pin selects either DAC A(active high) 
        # or DAC B.
        # cs = chip select
        # wr = write
        # self.outDACAB = Signal(1)
        # self.outWR = Signal(1)
        # self.outCS = Signal(1)

        # Both DACs can be simultaneously updated using the asynchronous 
        # LDAC(active high) input and can be cleared by using the 
        # asynchronous CLR(active high) input.
        # self.outLDAC = Signal(1)
        # self.outCLR = Signal(1)

        # low power mode(active high)
        # self.outPD = Signal(1)


    # python type annotation .. -> Module:
    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # can i for loop this ?

        m.d.comb += self.outDB0.eq(self.si[0])
        m.d.comb += self.outDB1.eq(self.si[1])
        m.d.comb += self.outDB2.eq(self.si[2])
        m.d.comb += self.outDB3.eq(self.si[3])
        m.d.comb += self.outDB4.eq(self.si[4])
        m.d.comb += self.outDB5.eq(self.si[5])
        m.d.comb += self.outDB6.eq(self.si[6])
        m.d.comb += self.outDB7.eq(self.si[7])

        return m


    # return a list of public signals
    def ports(self) -> List[Signal]:
        return[self.si, self.outDB0, self.outDB1, self.outDB2, self.outDB3, self.outDB4, self.outDB5, self.outDB6, self.outDB7]


if __name__ == "__main__":
    parser = main_parser()
    args = parser.parse_args()

    # define top level module
    m = Module()

    # add sub-modules to it and give it a name, so it will display in gtkwave
    m.submodules.AD7302DAC = AD7302DAC = AD7302()
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

    # def 


    # these lines are important because they are our input lines and if we want to trace them 
    # we need to init them here
    x = Signal(8)

    m.d.comb += AD7302DAC.si.eq(x)

    sim = Simulator(m)

    # a generator, so requires a yield
    def count_process():
        yield x.eq(0x00)
        # no clock here so use a Delay()
        yield Delay(1e-6)
        yield x.eq(0x05)
        yield Delay(1e-6)
        yield x.eq(0x50)
        yield Delay(1e-6)


    sim.add_process(count_process)
    # creates files which you open with gtkwave countTest.vcd 
    with sim.write_vcd("AD7302DAC.vcd", "AD7302DAC.gtkw", traces=[x] + AD7302DAC.ports()):
        sim.run()
