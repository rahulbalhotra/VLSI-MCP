// Simple FIFO Module for RTL parsing and verification testing
module fifo #(
    parameter DEPTH = 8,
    parameter WIDTH = 8
) (
    input  wire             clk,
    input  wire             rst_n,
    input  wire             w_en,
    input  wire             r_en,
    input  wire [WIDTH-1:0] data_in,
    output reg  [WIDTH-1:0] data_out,
    output reg              full,
    output reg              empty
);

    // State parameters for FSM
    localparam STATE_IDLE = 2'b00;
    localparam STATE_BUSY = 2'b01;
    localparam STATE_FULL = 2'b10;

    reg [1:0] state, next_state;
    reg [2:0] count;
    reg [2:0] wr_ptr;
    reg [2:0] rd_ptr;
    reg [WIDTH-1:0] mem [DEPTH-1:0];

    // FSM State Register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= STATE_IDLE;
        end else begin
            state <= next_state;
        end
    end

    // FSM Next State Logic
    always @(*) begin
        case (state)
            STATE_IDLE: begin
                if (full && w_en && !r_en)
                    next_state = STATE_FULL;
                else if (w_en || r_en)
                    next_state = STATE_BUSY;
                else
                    next_state = STATE_IDLE;
            end
            STATE_BUSY: begin
                if (empty)
                    next_state = STATE_IDLE;
                else if (full)
                    next_state = STATE_FULL;
                else
                    next_state = STATE_BUSY;
            end
            STATE_FULL: begin
                if (r_en)
                    next_state = STATE_BUSY;
                else
                    next_state = STATE_FULL;
            end
            default: next_state = STATE_IDLE;
        end
    end

    // Count and Pointers logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 0;
            wr_ptr <= 0;
            rd_ptr <= 0;
            full <= 0;
            empty <= 1;
        end else begin
            if (w_en && !full) begin
                mem[wr_ptr] <= data_in;
                wr_ptr <= wr_ptr + 1;
            end
            if (r_en && !empty) begin
                data_out <= mem[rd_ptr];
                rd_ptr <= rd_ptr + 1;
            end

            // Update count
            if (w_en && !r_en && !full) begin
                count <= count + 1;
            end else if (r_en && !w_en && !empty) begin
                count <= count - 1;
            end

            // Flags update
            full  <= (count == DEPTH - 1 && w_en && !r_en) ? 1 : (count == DEPTH);
            empty <= (count == 1 && r_en && !w_en) ? 1 : (count == 0);
        end
    end

endmodule
