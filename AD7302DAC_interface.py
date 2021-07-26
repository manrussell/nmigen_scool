###############################################################################
# GENERAL DESCRIPTION:
# This module will interface between the output of the JT51 synth and a a DAC i
# have lying around at home
#
###############################################################################
# AD7302 DAC:
# The AD7302 is a dual, 8-bit voltage out DAC that operates
# from a single +2.7 V to +5.5 V supply. Its on-chip precision output buffers
# allow the DAC outputs to swing rail to rail. TheAD7302 has a parallel
# microprocessor and DSP-compatibleinterface with high speed registers and
# double buffered interfacelogic.
### AD7302 DAC:
# Parallel Data Inputs. Eight-bit data is loaded to the input register
# of the AD7302 under the control of CS and WR
### CONTROL LOGIC:
# On the rising edge of the WR signal, the values on pins D7-D0 will be
# latched into the Input register. When the signal LDAC is low, the data in
# the Input register is transferred to the DAC register and a new
# D/A conversion is started.
# ,max clock freq of DAC is ...
### Pins (Full list):
# DB0-DB7,  8-bit parallel data input
# DACAB,    # DAC A(active high) or B (A=left, R=write)
# WR,       write enable, (active high)
# LDAC,     Load (both)DAC's, (active high), asynchronous
# PD,       Power Down, (active high)...pull to ground (electrically) on PCB
# CS,       Chip Select, (active high)...pull to ground (electrically) on PCB
# CLR,      Clear, (active high), asynchronous...pull to ground (electrically) on PCB
#
###############################################################################
# JT51 SYNTH:
# outs from Ym2151/JT51 are prefixed i_ for input
# JT51 output data rate of 55kHz, stereo, 16 bits per channel.
### Pins (Full list):
#   o_ct1       General purpose output, configurable through MMR
#   o_ct2       General purpose output, configurable through MMR
#   o_irq_n     Active (low) when timer overflow. Only if programmed to.
#   o_p1        clk/2. This is the clock at which sound gets synthesised
#   o_sample    Indicates that new output data is ready.
#   o_xleft     Audio output with full 16 bit resolution. Signed
#   o_xright
###############################################################################

from typing import List

from nmigen import *
from nmigen.build import Platform
from nmigen.cli import main_parser
from nmigen.sim import Simulator, Delay

class AD7302(Elaboratable):
    def __init__(self):
        # JT51
        self.i_xL           = Signal(16) # Audio out 16 bit resolution. Signed.
        self.i_xR           = Signal(16) # Audio out 16 bit resolution. Signed.
        self.i_sample_valid = Signal(1)  # Indicates new output data is ready, 1 * clock pulse high.
        self.i_p1           = Signal(1)  # clock from JT51

        # AD7302 DAC
        # Parallel Data.
        self.o_DB0 = Signal(1)
        self.o_DB1 = Signal(1)
        self.o_DB2 = Signal(1)
        self.o_DB3 = Signal(1)
        self.o_DB4 = Signal(1)
        self.o_DB5 = Signal(1)
        self.o_DB6 = Signal(1)
        self.o_DB7 = Signal(1)
        # control logic
        self.o_DACAB    = Signal(1) # DAC A or B (A=left, R=write)
        self.o_WR       = Signal(1)
        self.o_LDAC     = Signal(1)


    # python type annotation .. -> Module:
    def elaborate(self, platform: Platform) -> Module:
        m = Module()


        # i think this should init the state machine, but nmight be depreciated
        # self.submodules.fsm = FSM(reset_state="IDLE")

#TODO: How to use rising and failing clock edges??
#
        # FSM which writes the data from the JT51 to the AD7302 DAC
        with m.FSM(name="transmit_fsm"):

            with m.State("READ_A"): # idle state
                m.d.comb += self.o_WR.eq(0)
                m.d.comb += self.o_LDAC.eq(0)
                m.d.comb += self.o_DACAB.eq(1)

                # DAC_A == left channel audio
                # if m.d.comb seems to reset itself on the next clock
                # by making it m.d.sync it latches the value -must add a register? 
                m.d.sync += self.o_DB0.eq(self.i_xL[0])
                m.d.sync += self.o_DB1.eq(self.i_xL[1])
                m.d.sync += self.o_DB2.eq(self.i_xL[2])
                m.d.sync += self.o_DB3.eq(self.i_xL[3])
                m.d.sync += self.o_DB4.eq(self.i_xL[4])
                m.d.sync += self.o_DB5.eq(self.i_xL[5])
                m.d.sync += self.o_DB6.eq(self.i_xL[6])
                m.d.sync += self.o_DB7.eq(self.i_xL[7])

                with m.If(self.i_sample_valid):
                    # this could work and you remove a state by sampling here
                    # m.d.comb += self.o_WR.eq(1)
                    m.next = "WRITE_A"

            with m.State("WRITE_A"):
                # latch registers
                m.d.comb += self.o_WR.eq(1)

                # hmmm if m.d.comb why do i have to stipulate this here? 
                # it doesn't seem to hold the previous value from 'READ_A'
                # instead it returns to zero
                # m.d.sync += self.o_DB0.eq(self.i_xL[0])
                # m.d.sync += self.o_DB1.eq(self.i_xL[1])
                # m.d.sync += self.o_DB2.eq(self.i_xL[2])
                # m.d.sync += self.o_DB3.eq(self.i_xL[3])
                # m.d.sync += self.o_DB4.eq(self.i_xL[4])
                # m.d.sync += self.o_DB5.eq(self.i_xL[5])
                # m.d.sync += self.o_DB6.eq(self.i_xL[6])
                # m.d.sync += self.o_DB7.eq(self.i_xL[7])
                # same here
                m.d.comb += self.o_DACAB.eq(1)
                m.next = "CHANGE_AB"

            with m.State("CHANGE_AB"):      # can i remove this state 
                # stop writing to register - or ... is this necessary? does it sample on clock rising and that's it?
                m.d.comb += self.o_WR.eq(0)
                # write to DAC_B
                m.d.comb += self.o_DACAB.eq(0)
                m.next = "READ_B"

            with m.State("READ_B"):
                m.d.sync += self.o_DB0.eq(self.i_xR[0])
                m.d.sync += self.o_DB1.eq(self.i_xR[1])
                m.d.sync += self.o_DB2.eq(self.i_xR[2])
                m.d.sync += self.o_DB3.eq(self.i_xR[3])
                m.d.sync += self.o_DB4.eq(self.i_xR[4])
                m.d.sync += self.o_DB5.eq(self.i_xR[5])
                m.d.sync += self.o_DB6.eq(self.i_xR[6])
                m.d.sync += self.o_DB7.eq(self.i_xR[7])
                m.next = "WRITE_B"

            with m.State("WRITE_B"):
                # latch registers
                m.d.comb += self.o_WR.eq(1)
                m.next = "DA_CONVERT"

            with m.State("DA_CONVERT"):
                # send data from DAC registers to be converted by the DAC
                m.d.comb += self.o_LDAC.eq(1)
                m.d.comb += self.o_WR.eq(0)
                m.next = "READ_A"

        return m


    # return a list of public signals
    def ports(self) -> List[Signal]:
        return[self.i_xL, self.i_xR, self.i_p1, self.i_sample_valid, \
        self.o_DB0, self.o_DB1, self.o_DB2, self.o_DB3, self.o_DB4,  \
        self.o_DB5, self.o_DB6, self.o_DB7, self.o_DACAB, self.o_WR, \
        self.o_LDAC]



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
    # put args into parser, add module, add ports we are interested in 
    # outputting to a trace if doing simulation or yo-sis if doing formal 
    # verification
    # main_runner(parser, args, m, ports=[] + adder.ports())

    #
    #
    # for simulating
    #

    # these lines are important because they are our input lines and if we 
    # want to trace them we need to init them here
    x = Signal(16)
    icIn = Signal(1)

    m.d.comb += AD7302DAC.i_xL.eq(x)
    m.d.comb += AD7302DAC.i_xR.eq(~x)
    m.d.sync += AD7302DAC.i_sample_valid.eq(icIn)

    sim = Simulator(m)
    sim.add_clock(1e-6)

    # a generator, so requires a yield
    def count_process():
            #####
        #set JT51 left and Right to values ready to send to DAC
        yield x.eq(0xAA)
        # send sample_valid signal, high for one clock pulse
        yield icIn.eq(1)
        yield
        # release sample_valid, set low
        yield icIn.eq(0)
        yield
        # go gadget go
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        yield
        
        #set JT51 left and Right to values ready to send to DAC
        yield x.eq(0x05)
        # send sample_valid signal, high for one clock pulse
        yield icIn.eq(1)
        yield
        # release sample_valid, set low
        yield icIn.eq(0)
        yield
        # go gadget go
        yield
        yield
        yield
        yield
        yield

        #set JT51 left and Right to values ready to send to DAC
        yield x.eq(0xFE)
        # send sample_valid signal, high for one clock pulse
        yield icIn.eq(1)
        yield
        # release sample_valid, set low
        yield icIn.eq(0)
        yield
        # go gadget go
        yield
        yield
        yield
        yield
        yield
        yield
        yield


    sim.add_sync_process(count_process)
    # sim.add_process(count_process)
    # creates files which you open with gtkwave countTest.vcd
    with sim.write_vcd("AD7302DAC.vcd", "AD7302DAC.gtkw", traces=[x] + AD7302DAC.ports()):
        sim.run()
