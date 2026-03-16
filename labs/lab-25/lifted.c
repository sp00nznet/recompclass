/*
 * Lab 25: Hand-Lifted Z80 Subroutine
 *
 * Original Z80 assembly:
 *
 *   ; checksum(HL=start address, B=byte count) -> A=result
 *   checksum:
 *       XOR A           ; A = A ^ A = 0, sets Z=1, clears N/H/C
 *   .loop:
 *       ADD A, (HL)     ; A = A + mem[HL], update Z/H/C, clear N
 *       INC HL          ; HL = HL + 1 (flags not affected by INC rr)
 *       DEC B           ; B = B - 1, update Z/N/H, C unchanged
 *       JR NZ, .loop    ; if Z == 0, jump to .loop
 *       RET             ; return, result in A
 *
 * Translate each instruction to C below.
 */

#include "z80_runtime.h"

/* The global memory array */
uint8_t z80_mem[Z80_MEM_SIZE];


void lifted_checksum(z80_regs_t *regs) {
    /*
     * XOR A
     * A = A ^ A (always 0). Flags: Z=1, N=0, H=0, C=0.
     */
    // TODO: Set regs->A to 0.
    // TODO: Set flags: F_Z=1, F_N=0, F_H=0, F_C=0.


    /*
     * .loop:
     * We use a C label + goto to match the Z80 control flow.
     * (In a real lifter you'd use a while loop or structured control flow,
     * but goto is the most literal translation.)
     */
loop:

    /*
     * ADD A, (HL)
     * A = A + mem[HL]. Flags: Z=(result==0), N=0,
     * H=((A&0xF)+(mem[HL]&0xF)>0xF), C=(sum>0xFF).
     */
    // TODO: Read the byte at z80_mem[z80_get_HL(regs)].
    // TODO: Compute the sum (use a temporary uint16_t to detect carry).
    // TODO: Update flags: F_Z, F_N=0, F_H, F_C.
    // TODO: Store the low 8 bits of the sum back into regs->A.


    /*
     * INC HL
     * HL = HL + 1. No flags affected (INC on a register pair
     * does not change flags on the Z80).
     */
    // TODO: Increment the HL register pair by 1.
    //       Hint: z80_set_HL(regs, z80_get_HL(regs) + 1);


    /*
     * DEC B
     * B = B - 1. Flags: Z=(B==0), N=1, H=((old_B&0xF)==0), C unchanged.
     */
    // TODO: Compute H flag before modifying B.
    // TODO: Decrement regs->B by 1.
    // TODO: Update flags: F_Z, F_N=1, F_H. Do NOT change F_C.


    /*
     * JR NZ, .loop
     * If Z flag is not set, jump back to .loop.
     */
    // TODO: if (!regs->F_Z) goto loop;


    /*
     * RET
     * Just return from the C function.
     */
    return;
}
