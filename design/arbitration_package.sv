// SystemVerilog Arbitration Package
package arbitration_package;

    // Define priority modes
    typedef enum logic [1:0] {
        PRIORITY_FIXED      = 2'b00,
        PRIORITY_ROUND_ROBIN = 2'b01,
        PRIORITY_RANDOM      = 2'b10
    } priority_mode_t;

    // Configuration structure for arbiter parameters
    typedef struct {
        int num_clients;
        priority_mode_t mode;
    } arb_config_t;

endpackage : arbitration_package
