# task_logic.py

import time

class TaskLogic:
    @staticmethod
    def run_step(step_number):
        """Simulate a task that can fail."""
        print(f"Running step {step_number}...")
        time.sleep(1)  # Simulate work

        # Simulate an error at step 3
        # if step_number == 3:
        #     raise Exception("Error encountered during step 3!")

        return True  # Indicate successful execution
