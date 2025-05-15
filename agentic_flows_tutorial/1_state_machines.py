 # 1. State Management & State Machines for Agentic Flows

from enum import Enum, auto
from typing import Callable, Dict, Any, Optional

# --- What are State Machines? ---
# A state machine is a behavioral model. It consists of a finite number of states
# and transitions between these states. An agent or system can only be in one state
# at a time (the "current state"). A transition from one state to another is
# typically triggered by an event or a condition.

# --- Why use State Machines for Agents? ---
# - **Structured Control Flow:** Provides a clear and manageable way to define complex agent behaviors.
# - **Predictability:** Makes it easier to understand and predict what an agent will do in different situations.
# - **Maintainability:** Changes to agent logic can often be localized to specific states or transitions.
# - **Explicit State Management:** Clearly defines all possible states the agent can be in.
# - **Foundation for Complex Logic:** Can be used to model conversations, task execution processes, etc.

# --- Components of a Simple State Machine ---
# 1. **States:** A defined set of possible states (e.g., using an Enum).
# 2. **Initial State:** The state the machine starts in.
# 3. **Transitions:** Rules that define how to move from one state to another based on events/inputs.
# 4. **Actions (Optional):** Functions to execute upon entering a state, exiting a state, or during a transition.
# 5. **Events/Inputs:** Triggers that cause state transitions.

# --- Example: A Simple Order Processing Agent State Machine ---

# 1. Define States
class OrderState(Enum):
    PENDING_PAYMENT = auto()    # Waiting for payment confirmation
    AWAITING_SHIPMENT = auto()  # Payment received, ready to ship
    SHIPPED = auto()            # Order has been shipped
    DELIVERED = auto()          # Order has been delivered
    CANCELLED = auto()          # Order was cancelled
    FAILED = auto()             # An unrecoverable error occurred

# Define Events (Inputs that trigger transitions)
class OrderEvent(Enum):
    PAYMENT_RECEIVED = auto()
    PAYMENT_FAILED = auto()
    ITEM_SHIPPED = auto()
    DELIVERY_CONFIRMED = auto()
    CANCEL_ORDER = auto()
    ERROR_OCCURRED = auto()


class AgentStateMachine:
    def __init__(self, initial_state: OrderState):
        self.current_state: OrderState = initial_state
        self._transitions: Dict[OrderState, Dict[OrderEvent, OrderState]] = {}
        self._on_enter_actions: Dict[OrderState, Callable[[Any], None]] = {}
        self._on_exit_actions: Dict[OrderState, Callable[[Any], None]] = {}
        print(f"State Machine initialized. Current state: {self.current_state.name}")

    def add_transition(self, from_state: OrderState, event: OrderEvent, to_state: OrderState):
        if from_state not in self._transitions:
            self._transitions[from_state] = {}
        self._transitions[from_state][event] = to_state

    def add_on_enter_action(self, state: OrderState, action: Callable[[Any], None]):
        """Register an action to be performed when entering a state."""
        self._on_enter_actions[state] = action

    def add_on_exit_action(self, state: OrderState, action: Callable[[Any], None]):
        """Register an action to be performed when exiting a state."""
        self._on_exit_actions[state] = action

    def handle_event(self, event: OrderEvent, event_data: Optional[Any] = None) -> bool:
        print(f"\nHandling Event: {event.name} (Data: {event_data})")
        if self.current_state in self._transitions and event in self._transitions[self.current_state]:
            old_state = self.current_state
            new_state = self._transitions[self.current_state][event]
            
            print(f"  Transitioning: {old_state.name} --({event.name})--> {new_state.name}")

            # Execute on_exit action for the old state
            if old_state in self._on_exit_actions:
                print(f"  Executing on_exit action for {old_state.name}...")
                self._on_exit_actions[old_state](event_data)

            self.current_state = new_state

            # Execute on_enter action for the new state
            if new_state in self._on_enter_actions:
                print(f"  Executing on_enter action for {new_state.name}...")
                self._on_enter_actions[new_state](event_data)
            
            return True
        else:
            print(f"  No transition defined for state {self.current_state.name} with event {event.name}. Event ignored.")
            return False

    def get_current_state(self) -> OrderState:
        return self.current_state

# --- Define actions for the Order Processing Agent ---
def notify_user_pending_payment(data):
    print(f"ACTION: User notified - Order {data.get('order_id', '')} is pending payment.")

def process_payment_and_prepare_shipment(data):
    print(f"ACTION: Payment processed for order {data.get('order_id', '')}. Preparing for shipment.")
    # In a real agent, this might trigger other API calls, database updates, etc.

def send_shipping_notification(data):
    print(f"ACTION: Shipping notification sent for order {data.get('order_id', '')} with tracking {data.get('tracking_id', '')}.")

def confirm_delivery_and_close_order(data):
    print(f"ACTION: Delivery confirmed for order {data.get('order_id', '')}. Order closed.")

def handle_cancellation(data):
    print(f"ACTION: Order {data.get('order_id', '')} cancelled. Processing refund if applicable.")

def log_failure(data):
    print(f"ACTION: Critical failure for order {data.get('order_id', '')}. Details: {data.get('error_details', '')}")

# --- Setup and run the State Machine ---
if __name__ == "__main__":
    print("--- State Machine Example: Order Processing Agent ---")
    order_agent = AgentStateMachine(initial_state=OrderState.PENDING_PAYMENT)

    # Define transitions
    order_agent.add_transition(OrderState.PENDING_PAYMENT, OrderEvent.PAYMENT_RECEIVED, OrderState.AWAITING_SHIPMENT)
    order_agent.add_transition(OrderState.PENDING_PAYMENT, OrderEvent.PAYMENT_FAILED, OrderState.FAILED)
    order_agent.add_transition(OrderState.PENDING_PAYMENT, OrderEvent.CANCEL_ORDER, OrderState.CANCELLED)
    
    order_agent.add_transition(OrderState.AWAITING_SHIPMENT, OrderEvent.ITEM_SHIPPED, OrderState.SHIPPED)
    order_agent.add_transition(OrderState.AWAITING_SHIPMENT, OrderEvent.CANCEL_ORDER, OrderState.CANCELLED) # Can cancel before shipping
    order_agent.add_transition(OrderState.AWAITING_SHIPMENT, OrderEvent.ERROR_OCCURRED, OrderState.FAILED)

    order_agent.add_transition(OrderState.SHIPPED, OrderEvent.DELIVERY_CONFIRMED, OrderState.DELIVERED)
    order_agent.add_transition(OrderState.SHIPPED, OrderEvent.ERROR_OCCURRED, OrderState.FAILED) # e.g., shipping issue

    # Define on_enter actions
    order_agent.add_on_enter_action(OrderState.PENDING_PAYMENT, notify_user_pending_payment)
    order_agent.add_on_enter_action(OrderState.AWAITING_SHIPMENT, process_payment_and_prepare_shipment)
    order_agent.add_on_enter_action(OrderState.SHIPPED, send_shipping_notification)
    order_agent.add_on_enter_action(OrderState.DELIVERED, confirm_delivery_and_close_order)
    order_agent.add_on_enter_action(OrderState.CANCELLED, handle_cancellation)
    order_agent.add_on_enter_action(OrderState.FAILED, log_failure)

    # Simulate a sequence of events for an order
    order_data_1 = {"order_id": "ORD123"}
    order_agent.handle_event(OrderEvent.PAYMENT_RECEIVED, event_data=order_data_1)
    
    shipping_data_1 = {**order_data_1, "tracking_id": "TRKXYZ789"}
    order_agent.handle_event(OrderEvent.ITEM_SHIPPED, event_data=shipping_data_1)
    
    order_agent.handle_event(OrderEvent.DELIVERY_CONFIRMED, event_data=order_data_1)

    print(f"\nFinal state for ORD123: {order_agent.get_current_state().name}")

    # Simulate another order that fails
    print("\n--- Simulating another order that fails ---")
    order_agent_2 = AgentStateMachine(initial_state=OrderState.PENDING_PAYMENT)
    order_agent_2.add_transition(OrderState.PENDING_PAYMENT, OrderEvent.PAYMENT_FAILED, OrderState.FAILED)
    order_agent_2.add_on_enter_action(OrderState.FAILED, log_failure)

    order_data_2 = {"order_id": "ORD456", "error_details": "Credit card declined"}
    order_agent_2.handle_event(OrderEvent.PAYMENT_FAILED, event_data=order_data_2)
    print(f"\nFinal state for ORD456: {order_agent_2.get_current_state().name}")

    # Simulate an invalid event for current state
    order_agent.handle_event(OrderEvent.PAYMENT_RECEIVED, event_data=order_data_1) # ORD123 is already DELIVERED

# --- Key Takeaways for State Machines in Agents ---
# - Enums are great for defining states and events.
# - A dictionary can map (current_state, event) -> next_state for transitions.
# - Actions can be associated with state entries, exits, or transitions themselves.
# - This simple implementation can be extended with features like: 
#   - Guard conditions for transitions (additional checks before a transition occurs).
#   - More complex event data handling.
#   - Hierarchical state machines (states within states).
# - Libraries like `transitions` (pytransitions) can provide more advanced features out-of-the-box.
# - For agentic flows, the "actions" are where the agent would call its tools, 
#   update its internal knowledge, or communicate with users/other systems.
