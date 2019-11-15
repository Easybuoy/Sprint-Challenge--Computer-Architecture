"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.ram = [0] * 256

        # Register (R0 - R7)
        self.register = [0] * 8
        self.running = True
        # Program Counter
        # self.pc = self.register[0]

        # Instruction Register
        self.ir = None

        # Stack Pointer
        self.sp = 7  # Stack pointer R7
        self.op_pc = False
        self.equal = 0

        # set up branchtable
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CMP] = self.handle_cmp
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[JMP] = self.handle_jmp

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        if len(sys.argv) != 2:
            print("usage: ls8.py <filename>")
            sys.exit(1)
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()

                    if len(num) == 0:
                        continue

                    value = int(num, 2)

                    self.ram[address] = value

                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.load()
        while self.running:
            self.ir = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.branchtable[self.ir](operand_a, operand_b)

    def handle_ldi(self, op_a, op_b):
        self.reg[op_a] = op_b
        self.pc += 3

    def handle_prn(self, op_a, op_b):
        print(self.reg[op_a])
        self.pc += 2

    def handle_mul(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)
        self.pc += 3

    def handle_push(self, op_a, op_b):
        reg = self.ram_read(self.pc + 1)
        val = self.reg[reg]
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], val)
        self.pc += 2

    def handle_pop(self, op_a, op_b):
        reg = self.ram_read(self.pc + 1)
        val = self.ram_read(self.reg[self.sp])

        self.reg[reg] = val
        self.reg[self.sp] += 1
        self.pc += 2

    def handle_hlt(self, op_a, op_b):
        self.running = False

    def handle_cmp(self, op_a, op_b):
        if self.reg[op_a] == self.reg[op_b]:
            self.equal = 1
        else:
            self.equal = 0
        self.op_pc = False
        if not self.op_pc:
            self.pc += 3

    def handle_jeq(self, op_a, op_b):
        if self.equal == 1:
            self.pc = self.reg[op_a]
            self.op_pc = True
        if not self.op_pc:
            self.pc += 2

    def handle_jne(self, op_a, op_b):
        if self.equal == 0:
            self.pc = self.reg[op_a]
            self.op_pc = True
        if not self.op_pc:
            self.pc += 2

    def handle_jmp(self, op_a, op_b):
        self.pc = self.reg[op_a]
        self.op_pc = True
        if not self.op_pc:
            self.pc += 2

    def ram_read(self, addr):
        return self.ram[addr]

    def ram_write(self, addr, value):
        self.ram[addr] = value


cpu = CPU()
cpu.run()
