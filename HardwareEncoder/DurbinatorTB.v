`timescale 1ns/100ps
`define MY_SIMULATION 1
`include "Quantizer.v"
`define DFP(X) $bitstoshortreal(X)

module DurbinatorTB;

reg clk, ena, rst;
integer i, outfile;
integer cycles;

wire [31:0] alpha, k, error, model;
wire done;
reg [31:0] acf;
reg acf_valid;
wire valid;
wire [3:0] m;

wire signed [31:0] quant_c;
wire q_valid;

Durbinator db(
    .iClock(clk),
    .iEnable(ena), 
    .iReset(rst),
    
    .iValid(acf_valid),
    .iACF(acf),
    .alpha(alpha),
    .error(error),
    .k(k),
    
    .oM(m),
    .oModel(model),
    .oValid(valid),
    .oDone(done)
    );

Quantizer q (
    .iClock(clk),
    .iEnable(ena),
    .iReset(rst),
    .iValid(valid),
    .iFloatCoeff(model),
    .oQuantizedCoeff(quant_c),
    .oValid(q_valid)
    );
    

always begin
    #0 clk = 0;
    #10 clk = 1;
    #10 cycles = cycles + 1;
end

initial begin
    cycles = 0;
    ena = 0; rst = 1;
    #30;
    #20;    
    
    ena = 1; rst = 0; acf_valid = 1;
    acf = 32'h0x3f800000;
    #20;
    acf = 32'h0x3f7f7bb8;
    #20;
    acf = 32'h0x3f7e0430;
    #20;
    acf = 32'h0x3f7b9f88;
    #20;
    acf = 32'h0x3f784f5a;
    #20;
    acf = 32'h0x3f742267;
    #20;
    acf = 32'h0x3f6f2663;
    #20;
    acf = 32'h0x3f696ae8;
    #20;
    acf = 32'h0x3f63029e;
    #20;
    acf = 32'h0x3f5bfe6b;
    #20;
    acf = 32'h0x3f54715b;
    #20;
    acf = 32'h0x3f4c6cdf;
    #20;
    acf = 32'h0x3f4401d3;
    #20;
    acf_valid = 0;

    outfile = $fopen("ld_coefficients.txt", "w");
    for (i = 0; i < 1200; i = i + 1) begin
        if (valid) begin
            $display("  %d  MODEL: %f", m, `DFP(model));
        end
        
        if (q_valid) begin
            $display("Q: %d Model: %d", m, quant_c);
            $fwrite(outfile, "%d %d\n", m, quant_c);
        end
        #20;
    end
    $stop;
    
end

endmodule