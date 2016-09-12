#!/usr/bin/env python

# Generate n-tap FIR filter

from math import *
import sys

log2 = lambda x: int(ceil(log(x, 2)))

order = int(sys.argv[1])

def generate_fir_filter(order):

    latency = log2(order) + 1

    def generate_adders(inputs):
        return (inputs / 2, int(ceil(inputs/2.0) - inputs/2))
        
    print """
    
module FIR{order}(
    input wire iClock,
    input wire iEnable,
    input wire iReset,
    
    input wire iLoad, 
    input wire signed [11:0] iQLP,
    
    input wire iValid,
    input wire signed [15:0] iSample,
    
    output wire signed [15:0] oResidual,
    output wire oValid
    );

parameter ORDER = {order};
parameter LATENCY = {latency} + ORDER;
parameter PRECISION = 12;

integer i;
reg signed [11:0] qlp_coeff [0:ORDER - 1];
reg signed [15:0] data[0:ORDER - 1];
reg [3:0] coeff_count;
reg [LATENCY:0] valid;
""".format(order=order, latency=latency)

    n_levels = log2(order)
    n_multipliers = order

    ############ Print the register declarations 

    registers = []
    inputs = ["level0_{i}".format(i=i) for i in range(0, n_multipliers)]

    registers.extend(inputs)
    for i in range(1, n_levels + 1):
        adders, regs = generate_adders(len(inputs))
        outputs = ["level{i}_{j}".format(i=i, j=j) for j in range(0, adders)]
        
        if (regs > 0):
            outputs.append("rlevel{i}_{jp1}".format(i=i,jp1=adders))
            
        registers.extend(outputs)
        inputs = outputs

    for r in registers:
        print "reg signed [`SHIFT + 16:0] %s;"%r
    for i in range(n_levels + 1):
        print "reg signed [15:0] data0_l%d;"%i
    
    print "reg signed [15:0] residual;"

    ############## Print the reset #############

    print """
assign oValid = valid[LATENCY];
assign oResidual = residual; // right shift the result

always @(posedge iClock) begin
    if (iReset) begin
        qlp_coeff[0] <= 0;
        data[0] <= 0;
        
        valid <= 0;
        coeff_count <= 0;
"""

    #for r in registers:
    #    print " "*7,
    #    print "%s <= 0;"%r
        
    print """
    end else if (iEnable) begin
        if (iLoad && coeff_count <= ORDER) begin
            qlp_coeff[0] <= iQLP;
            for (i = ORDER - 1; i > 0; i = i - 1) begin
                qlp_coeff[i] <= qlp_coeff[i - 1];
            end 
            coeff_count <= coeff_count + 1'b1;
        end else begin
            valid <= (valid << 1) | iValid;
            
            data[0] <= iSample;
            for (i = ORDER - 1; i > 0; i = i - 1) begin
                data[i] <= data[i - 1];
            end 
    """
    ############## Print the Adder Tree ##########

    for i in range(0, n_multipliers):
        print " "*11,
        print "level0_{i} <= qlp_coeff[{i}]*data[{i}]".format(i=i) + ";"
    print
    print " "*11,
    print "data0_l0 <= iSample;"

    for i in range(1, n_levels + 1):
        print " "*11,
        print "data0_l%d <= data0_l%d;"%(i, i - 1)
    
    
    inputs = ["level0_{i}".format(i=i) for i in range(0, n_multipliers)]
    for i in range(1, n_levels + 1):
        adders, registers = generate_adders(len(inputs))
        outputs = ["level{i}_{j}".format(i=i, j=j) for j in range(0, adders)]
        if (registers > 0):
            outputs.append("rlevel{i}_{jp1}".format(i=i,jp1=adders))
        print
        
        for a in range(0, adders*2, 2):
            print " "*11,
            print outputs[a/2], "<=", inputs[a], "+", inputs[a+1] + ";"
        for r in range(0,registers):
            print " "*11,
            print outputs[-1], "<=", inputs[-1] + ";"
        
        inputs = outputs
    
    print
    print " "*11,
    print "residual <= data0_l{n_levels} - ({sum} >> `SHIFT);".format(n_levels=n_levels, sum=inputs[-1])
        

    print " "*7, "end"
    print " "*3, "end"

    print "end"

    print "endmodule"
    
print """
/* This code has been autogenerated by "generate_fir.py".
 * Modify at your own risk
 */
 
 
`define SHIFT 10
 """
    
for i in range(1, order + 1):
    generate_fir_filter(i)