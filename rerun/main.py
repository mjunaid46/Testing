import pickle
import sys
import importlib
import order_processing_logic  # Import the order processing logic module


def save_state(data, filename="order_state.pkl"):
    """Save the current processing state to a Pickle file."""
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def load_state(filename="order_state.pkl"):
    """Load the saved processing state from a Pickle file."""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


class OrderProcessingWithRetry:
    def __init__(self):
        self.state = load_state() or {"step": 1, "retry_count": 0, "completed_steps": []}
        self.max_steps = 5
        self.max_retries = 3

    def reload_task_logic(self):
        """Dynamically reload the order_processing_logic module."""
        if "order_processing_logic" in sys.modules:
            del sys.modules["order_processing_logic"]  # Remove from cache
        global order_processing_logic
        importlib.import_module("order_processing_logic")  # Reimport fresh module
        order_processing_logic = sys.modules["order_processing_logic"]  # Update the reference

    def rerun_steps(self, steps_to_rerun):
        """Recursively re-run selected steps."""
        for step_to_rerun in steps_to_rerun:
            if step_to_rerun in self.state["completed_steps"]:
                print(f"Re-running Step {step_to_rerun}...")
                self.reload_task_logic()  # Reload the logic dynamically
                try:
                    success = order_processing_logic.process_step(step_to_rerun)
                    if success:
                        print(f"Step {step_to_rerun} re-executed successfully!")
                except Exception as e:
                    print(f"Error during re-run of Step {step_to_rerun}: {e}")
                    # Recursive prompt for retrying failed re-run
                    new_rerun_steps = input(
                        f"Enter step numbers to re-run from completed steps {self.state['completed_steps']} (comma-separated), or press Enter to skip: "
                    ).strip()
                    if new_rerun_steps:
                        try:
                            steps = [int(s.strip()) for s in new_rerun_steps.split(",")]
                            self.rerun_steps(steps)  # Recursive call
                        except ValueError:
                            print("Invalid input. Please enter step numbers as comma-separated values.")
                    return  # Exit after handling the failure

            else:
                print(f"Step {step_to_rerun} is not in the completed steps.")

    def run(self):
        while self.state["step"] <= self.max_steps:
            try:
                if self.state["step"] in self.state["completed_steps"]:
                    print(f"Step {self.state['step']} already completed. Skipping...")
                    self.state["step"] += 1
                    save_state(self.state)
                    continue

                print(f"Processing Step {self.state['step']} (Retry {self.state['retry_count']} of {self.max_retries})...")
                self.reload_task_logic()  # Reload the task logic dynamically

                # Run the task logic for the current step
                success = order_processing_logic.process_step(self.state["step"])

                if success:
                    self.state["completed_steps"].append(self.state["step"])
                    self.state["step"] += 1
                    self.state["retry_count"] = 0
                    save_state(self.state)
                    print(f"Step {self.state['step'] - 1} completed successfully!")

            except Exception as e:
                print(f"Error: {e}. You can re-run any previous steps or press Enter to continue.")
                rerun_steps = input(
                    f"Enter step numbers to re-run from completed steps {self.state['completed_steps']} (comma-separated), or press Enter to skip: "
                ).strip()

                if rerun_steps:
                    try:
                        steps_to_rerun = [int(s.strip()) for s in rerun_steps.split(",")]
                        self.rerun_steps(steps_to_rerun)  # Handle re-runs
                    except ValueError:
                        print("Invalid input. Please enter step numbers as comma-separated values.")

                self.state["retry_count"] += 1
                if self.state["retry_count"] > self.max_retries:
                    print(f"Maximum retries reached for Step {self.state['step']}. Skipping to the next step.")
                    self.state["step"] += 1
                    self.state["retry_count"] = 0

                save_state(self.state)
                continue

        print("Order processing completed successfully!")


if __name__ == "__main__":
    order_processor = OrderProcessingWithRetry()
    order_processor.run()
