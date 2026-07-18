// SystemVerilog Arbiter Module
import arbitration_package::*;

module arbiter #(
    parameter int NUM_CLIENTS = 4,
    parameter priority_mode_t MODE = PRIORITY_FIXED
) (
    input  logic                   clk,
    input  logic                   rst_n,
    input  logic [NUM_CLIENTS-1:0] req,
    output logic [NUM_CLIENTS-1:0] gnt,
    output logic                   any_gnt
);

    // State encoding for Round-Robin pointer
    logic [NUM_CLIENTS-1:0] rr_ptr;
    logic [NUM_CLIENTS-1:0] gnt_fixed;
    logic [NUM_CLIENTS-1:0] gnt_rr;
    
    //---------------------------------------------------------
    // 1. Fixed Priority Arbiter Logic
    // Client 0 has the highest priority, Client NUM_CLIENTS-1 the lowest
    //---------------------------------------------------------
    always_comb begin
        gnt_fixed = '0;
        for (int i = 0; i < NUM_CLIENTS; i++) begin
            if (req[i]) begin
                gnt_fixed[i] = 1'b1;
                break; // First match wins
            end
        end
    end

    //---------------------------------------------------------
    // 2. Round-Robin Arbiter Logic
    // Pointer rotates to the next client after a grant is accepted
    //---------------------------------------------------------
    
    // Rotate pointer on grant
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rr_ptr <= 1; // Default to client 0
        end else if (any_gnt) begin
            // Rotate left by 1 bit circular
            rr_ptr <= {rr_ptr[NUM_CLIENTS-2:0], rr_ptr[NUM_CLIENTS-1]};
        end
    end

    // Round-robin grant generation (masked request priority search)
    always_comb begin
        gnt_rr = '0;
        // Search starting from rr_ptr position circular
        for (int i = 0; i < NUM_CLIENTS; i++) begin
            int idx;
            idx = (i + rr_ptr) % NUM_CLIENTS;
            if (req[idx]) begin
                gnt_rr[idx] = 1'b1;
                break;
            end
        end
    end

    //---------------------------------------------------------
    // 3. Mode Selection & Outputs
    //---------------------------------------------------------
    always_comb begin
        if (MODE == PRIORITY_ROUND_ROBIN) begin
            gnt = gnt_rr;
        end else begin
            gnt = gnt_fixed;
        end
        any_gnt = (gnt != '0);
    end

endmodule
