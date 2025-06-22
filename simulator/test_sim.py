import json
import os
from lc3_sim import LC3_VM

class Colors:
    """A class to hold ANSI color codes for terminal output."""
    HEADER = '\033[95m'  # Purple
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m' # Green
    WARNING = '\033[93m'
    FAIL = '\033[91m'    # Red
    ENDC = '\033[0m'     # Resets the color to default
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_test_suite():
    # This line helps enable ANSI color support on some Windows terminals
    os.system('') 
    
    test_dir = "../tests"
    test_files = [f for f in os.listdir(test_dir) if f.endswith('.json')]
    total_passed = 0
    total_failed = 0

    for file_name in test_files:
        with open(os.path.join(test_dir, file_name), 'r') as f:
            data = json.load(f)
            instruction = data['instruction']
            print(f"{Colors.HEADER}--- Running tests for {instruction} ---{Colors.ENDC}")

            for test in data['tests']:
                # 1. Setup
                vm = LC3_VM()

                # Load initial registers
                if 'registers' in test['initial_state']:
                    for reg, val in test['initial_state']['registers'].items():
                        vm.registers[reg] = int(str(val), 0) 

                # Load initial memory
                if 'memory' in test['initial_state']:
                    for addr, val in test['initial_state']['memory'].items():
                        vm.memory[int(addr, 0)] = int(str(val), 0)

                # 2. Execution
                vm.run()

                # 3. Verification
                test_passed = True
                # Check final registers
                if 'registers' in test['final_state']:
                    for reg, expected_val in test['final_state']['registers'].items():
                        actual_val = vm.registers[reg]
                        expected_val = int(str(expected_val), 0)
                        if actual_val != expected_val:
                            if test_passed: # Print the failure header only once per test
                                print(f"  {Colors.FAIL}[FAIL]{Colors.ENDC} {test['name']}")
                            print(f"    - Register {Colors.BOLD}{reg}{Colors.ENDC}: expected {hex(expected_val)}, got {hex(actual_val)}")
                            test_passed = False
                
                # (Add a similar loop here to check final_state.memory for ST, etc.)

                if test_passed:
                    print(f"  {Colors.OKGREEN}[PASS]{Colors.ENDC} {test['name']}")
                    total_passed += 1
                else:
                    total_failed += 1
    
    print(f"\n{Colors.BOLD}--- Test Summary ---{Colors.ENDC}")
    passed_color = Colors.OKGREEN if total_failed == 0 else Colors.WARNING
    print(f"Passed: {passed_color}{total_passed}{Colors.ENDC}, Failed: {Colors.FAIL}{total_failed}{Colors.ENDC}")


if __name__ == '__main__':
    run_test_suite()