// Formal Verification Assertions for Arbiter Design
module fv_arbiter #(
    parameter int NUM_CLIENTS = 4
) (
    input  logic                   clk,
    input  logic                   rst_n,
    input  logic [NUM_CLIENTS-1:0] req,
    input  logic [NUM_CLIENTS-1:0] gnt,
    input  logic                   any_gnt
);

    // Default clocking block for formal tool properties
    default clocking @(posedge clk); endclocking

    //---------------------------------------------------------
    // Property 1: Mutual Exclusion
    // At most one grant can be active in any cycle
    //---------------------------------------------------------
    property p_mutual_exclusion;
        $onehot0(gnt); // 0 or 1 bits set
    endproperty
    a_mutual_exclusion: assert property (p_mutual_exclusion);
    c_mutual_exclusion: cover property (p_mutual_exclusion);

    //---------------------------------------------------------
    // Property 2: Grant Validity
    // A client can only receive a grant if it requested it
    //---------------------------------------------------------
    property p_grant_validity(int client_idx);
        gnt[client_idx] |-> req[client_idx];
    endproperty

    generate
        for (genvar i = 0; i < NUM_CLIENTS; i++) begin : gen_grant_validity
            a_grant_validity: assert property (p_grant_validity(i));
        end
    endgenerate

    //---------------------------------------------------------
    // Property 3: Fair Service (Liveness check)
    // If a client requests, it should eventually receive a grant
    //---------------------------------------------------------
    property p_fair_service(int client_idx);
        req[client_idx] |-> s_eventually gnt[client_idx];
    endproperty

    generate
        for (genvar i = 0; i < NUM_CLIENTS; i++) begin : gen_fair_service
            a_fair_service: assert property (p_fair_service(i));
        end
    endgenerate

    //---------------------------------------------------------
    // Property 4: No Spurious Grant Flag
    // any_gnt should be high if and only if gnt is not zero
    //---------------------------------------------------------
    property p_any_gnt_valid;
        any_gnt == (gnt != '0);
    endproperty
    a_any_gnt_valid: assert property (p_any_gnt_valid);

endmodule
