import pickle
import time
import sys
import importlib
import order_processing_logic  # Import the order processing logic module

def save_state(data, filename="order_state.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_state(filename="order_state.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

class OrderProcessingWithDependencies:
    def __init__(self):
        self.state = load_state() or {"step": 1, "retry_count": 0}
        self.max_steps = 5
        self.max_retries = 3

    def reload_task_logic(self):
        """Dynamically reload the order_processing_logic module."""
        if "order_processing_logic" in sys.modules:
            del sys.modules["order_processing_logic"]  # Remove from cache
        global order_processing_logic
        importlib.import_module("order_processing_logic")  # Reimport fresh module
        order_processing_logic = sys.modules["order_processing_logic"]  # Update the reference

    def get_dependencies(self, step):
        """Return a list of steps that are dependent on the current step."""
        dependencies = {
            2: [1],  # Step 2 depends on Step 1
            3: [1, 2],  # Step 3 depends on Steps 1 and 2
            4: [1,3],  # Step 4 depends on Steps 1, 2, and 3
            5: [1, 2, 3, 4],  # Step 5 depends on Steps 1, 2, 3, and 4
        }
        return dependencies.get(step, [])

    import time

    def retry_step_with_dependencies(self, step):
        """Retry a specific step and its dependencies, ensuring no redundant retries."""
        print(f"Retrying Step {step} and its dependencies automatically (Retry {self.state['retry_count']} of {self.max_retries})...")

        # Get all dependencies for the current step
        dependencies = self.get_dependencies(step)
        self.reload_task_logic() 

        # Ensure that we don't re-run already completed steps
        completed_steps = {step for step in range(1, self.state['step']) if self.state.get(f"step_{step}_completed", False)}

        # Include the current step itself for retries
        steps_to_retry = dependencies + [step]
        steps_to_retry = [s for s in steps_to_retry if s not in completed_steps]

        if steps_to_retry:
            for dep_step in steps_to_retry:
                print(f"Retrying Step {dep_step}...")
                retry_attempts = 0
                while retry_attempts < self.max_retries:
                    try:
                        # Retry the step
                        success = order_processing_logic.process_step(dep_step)
                        if success:
                            print(f"Step {dep_step} completed successfully!")
                            self.state[f"step_{dep_step}_completed"] = True  # Mark as completed
                            save_state(self.state)
                            break  # Exit retry loop if successful
                        else:
                            raise Exception(f"Step {dep_step} failed again.")
                    except Exception as e:
                        retry_attempts += 1
                        print(f"Error during re-run of Step {dep_step}: {e}. Retry attempt {retry_attempts} of {self.max_retries}.")
                        if retry_attempts >= self.max_retries:
                            print(f"Max retry attempts reached for Step {dep_step}. Moving to the next step.")
                            raise  # Max retries reached, stop retrying
                        else:
                            time.sleep(2)  # Add a small delay before retrying


    def run_step(self, step):
        """Run a single step."""
        print(f"Processing Step {step}...")
        try:
            success = order_processing_logic.process_step(step)
            if success:
                self.state[f"step_{step}_completed"] = True  # Mark as completed
                save_state(self.state)
                print(f"Step {step} completed successfully!")
            else:
                raise Exception(f"Step {step} failed.")
        except Exception as e:
            print(f"Error: {e}. Resolve the issue and press Enter to continue.")
            input("Press Enter to resume...")  # Wait for user to resolve the issue
            self.state["retry_count"] += 1
            if self.state["retry_count"] > self.max_retries:
                print(f"Maximum retries reached for Step {step}. Skipping to the next step.")
                self.state["step"] += 1
                self.state["retry_count"] = 0
            save_state(self.state)
            self.retry_step_with_dependencies(step)  # Retry the failed step and its dependencies

    def run(self):
        while self.state["step"] <= self.max_steps:
            try:
                print(f"Processing Step {self.state['step']} (Retry {self.state['retry_count']} of {self.max_retries})...")
                self.reload_task_logic()  # Reload the task logic dynamically

                # Run the task logic for the current step
                success = order_processing_logic.process_step(self.state["step"])

                if success:
                    self.state["step"] += 1
                    self.state["retry_count"] = 0
                    save_state(self.state)
                    print(f"Step {self.state['step'] - 1} completed successfully!")

            except Exception as e:
                print(f"Error: {e}. Resolve the issue and press Enter to continue.")
                input("Press Enter to resume...")  # Wait for user to resolve the issue
                self.state["retry_count"] += 1

                if self.state["retry_count"] > self.max_retries:
                    print(f"Maximum retries reached for Step {self.state['step']}. Skipping to the next step.")
                    self.state["step"] += 1
                    self.state["retry_count"] = 0

                save_state(self.state)
                self.retry_step_with_dependencies(self.state["step"])  # Automatically retry the current step and its dependencies

        print("Order processing completed successfully!")

if __name__ == "__main__":
    order_processor = OrderProcessingWithDependencies()
    order_processor.run()
