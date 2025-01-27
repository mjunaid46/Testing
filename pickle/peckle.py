import pickle
import time

# Functions to persist state
def save_state(data, filename="state.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_state(filename="state.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# Task class with manual resolution
class TaskWithManualResolution:
    def __init__(self):
        self.state = load_state() or {"step": 1}  # Load state or start from step 1
        self.max_steps = 5

    def run_step(self, step_number):
        """Simulate a task that can fail."""
        print(f"Running step {step_number}...")
        time.sleep(1)  # Simulate work

        # Simulate an error at step 3
        if step_number == 3:
            raise Exception("Error encountered during step 3!")

        return True  # Indicate successful execution

    def run(self):
        while self.state["step"] <= self.max_steps:
            try:
                print(f"Starting step {self.state['step']}...")
                success = self.run_step(self.state["step"])

                # If the step succeeds, update the state and save
                if success:
                    self.state["step"] += 1
                    save_state(self.state)

            except Exception as e:
                print(f"Error: {e}. Resolve the issue and press Enter to continue.")
                input("Press Enter to resume...")  # Wait for user to press Enter
                continue  # Continue to retry the current step

        print("Task completed successfully!")

# Example usage
if __name__ == "__main__":
    task = TaskWithManualResolution()
    task.run()
