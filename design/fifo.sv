// -------------------------------------------------
// Copyright(c) LUBIS EDA GmbH, All rights reserved
// Contact: contact@lubis-eda.com
// -------------------------------------------------

`default_nettype none

module fifo #(
    parameter WIDTH = 4,
    parameter DEPTH = 4
)(
    input  logic             clk,
    input  logic             reset,
    input  logic             push,
    input  logic             pop,
    input  logic [WIDTH-1:0] data_in,
    output logic [WIDTH-1:0] data_out,
    output logic             empty,
    output logic             full
);

localparam POINTER_WIDTH = $clog2(DEPTH);

// Signals that point to a specific position inside the buffer
logic [POINTER_WIDTH-1:0] read_position;
logic [POINTER_WIDTH-1:0] write_position;

// The value of this signal shows how many slots in the buffer are used.
logic [POINTER_WIDTH-1:0] fifo_counter;

// Buffer where the data values are stored
logic [WIDTH-1:0][DEPTH-1:0] buffer;

// Combinational part of the design
assign data_out = buffer[read_position];
assign empty    = (fifo_counter == 0);
assign full     = (fifo_counter == DEPTH);

always_ff @(posedge clk or posedge reset)
begin
    if (reset) begin
        fifo_counter <= 0;
    end
    else if ( (!full && push) && !(!empty && pop))
       fifo_counter <= fifo_counter + POINTER_WIDTH'('d1);
    else if (!(!full && push) &&  (!empty && pop))
       fifo_counter <= fifo_counter - POINTER_WIDTH'('d1);
    else
       fifo_counter <= fifo_counter;
end

always_ff @(posedge clk or posedge reset)
begin
    if (reset) begin
        buffer <= 0;
    end
    else if (push && !full)
        buffer[write_position] <= data_in;
end

always_ff @(posedge clk or posedge reset)
begin
    if (reset) begin
        write_position <= 0;
        read_position  <= 0;
    end
    else begin
        if (!full && push) begin
            write_position <= write_position + POINTER_WIDTH'('d1);
        end

        if (!empty && pop) begin
            read_position  <= read_position + POINTER_WIDTH'('d1);
        end
    end
end

endmodule
