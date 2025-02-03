import numpy as np
import cvxpy as cp
import matplotlib.pyplot as plt
import streamlit as st

# Streamlit app title
st.title("OPERA Simulation")

# Sidebar for user inputs
st.sidebar.header("Simulation Parameters")

# Define system parameters
n_states = 2  # Number of state variables
n_inputs = 2  # Number of control variables
N = st.sidebar.slider("Prediction Horizon (N)", 5, 20, 10)  # Prediction horizon
sim_steps = st.sidebar.slider("Simulation Steps", 20, 100, 50)  # Simulation steps

# Define bounds for control variables (positive values)
u1_min = st.sidebar.slider("Control 1 Minimum", 0.0, 1.0, 0.0)  # Lower bound for u1
u1_max = st.sidebar.slider("Control 1 Maximum", 0.0, 2.0, 1.0)  # Upper bound for u1
u2_min = st.sidebar.slider("Control 2 Minimum", 0.0, 1.0, 0.0)  # Lower bound for u2
u2_max = st.sidebar.slider("Control 2 Maximum", 0.0, 1.0, 0.5)  # Upper bound for u2

# Define bounds for state variables (positive values)
x1_min = st.sidebar.slider("State 1 Minimum", 0.0, 2.0, 0.0)  # Lower bound for x1
x1_max = st.sidebar.slider("State 1 Maximum", 0.0, 3.0, 2.0)  # Upper bound for x1
x2_min = st.sidebar.slider("State 2 Minimum", 0.0, 2.0, 0.0)  # Lower bound for x2
x2_max = st.sidebar.slider("State 2 Maximum", 0.0, 2.0, 1.5)  # Upper bound for x2

# Define system dynamics (state update equations)
a1, a2 = 0.8, 0.1
b1, b2 = 0.5, 0.2
c1, c2 = 0.1, 0.7
d1, d2 = 0.3, 0.4

# Define the objective function weights
Q1 = st.sidebar.slider("Q1 (Weight for x1)", 0.1, 10.0, 1.0)  # Weight for x1
Q2 = st.sidebar.slider("Q2 (Weight for x2)", 0.1, 10.0, 1.0)  # Weight for x2
R1 = st.sidebar.slider("R1 (Weight for u1)", 0.1, 10.0, 1.0)  # Weight for u1
R2 = st.sidebar.slider("R2 (Weight for u2)", 0.1, 10.0, 1.0)  # Weight for u2

# Define a reference trajectory for the states (positive values)
x1_ref = 1.0 + 0.5 * np.sin(0.1 * np.arange(sim_steps + N))  # Reference for x1
x2_ref = 0.8 + 0.3 * np.cos(0.1 * np.arange(sim_steps + N))  # Reference for x2

# Initialize arrays to store results
x1_history = [0.5]  # Initial state x1 (positive)
x2_history = [0.3]  # Initial state x2 (positive)
u1_history = []
u2_history = []
objective_history = [0.0]  # Initial objective value

# MPC loop
for t in range(sim_steps):
    # Define optimization variables
    x1 = cp.Variable((1, N + 1))
    x2 = cp.Variable((1, N + 1))
    u1 = cp.Variable((1, N))
    u2 = cp.Variable((1, N))
    objective = cp.Variable((1, N + 1))

    # Define cost and constraints
    cost = 0
    constraints = []

    # Initial state constraint
    constraints += [x1[:, 0] == x1_history[-1], x2[:, 0] == x2_history[-1]]

    # Initial objective constraint
    constraints += [objective[:, 0] == objective_history[-1]]

    # Build the cost and constraints over the prediction horizon
    for k in range(N):
        # State update equations
        constraints += [
            x1[:, k + 1] == a1 * x1[:, k] + a2 * x2[:, k] + b1 * u1[:, k] + b2 * u2[:, k],
            x2[:, k + 1] == c1 * x1[:, k] + c2 * x2[:, k] + d1 * u1[:, k] + d2 * u2[:, k],
        ]

        # Objective function: depends on past values of state, control, and objective
        constraints += [
            objective[:, k + 1] == 0.9 * objective[:, k] + 0.1 * (x1[:, k] + x2[:, k] + u1[:, k] + u2[:, k])
        ]

        # Add state constraints (positive values)
        constraints += [
            x1[:, k] >= x1_min, x1[:, k] <= x1_max,
            x2[:, k] >= x2_min, x2[:, k] <= x2_max,
        ]

        # Add control input constraints (positive values)
        constraints += [
            u1[:, k] >= u1_min, u1[:, k] <= u1_max,
            u2[:, k] >= u2_min, u2[:, k] <= u2_max,
        ]

        # Add to cost function (track reference trajectory)
        cost += Q1 * (x1[:, k] - x1_ref[t + k])**2 + Q2 * (x2[:, k] - x2_ref[t + k])**2 + \
                R1 * (u1[:, k]**2) + R2 * (u2[:, k]**2) + \
                1.0 * (objective[:, k]**2)

    # Terminal cost (optional)
    cost += Q1 * (x1[:, N] - x1_ref[t + N])**2 + Q2 * (x2[:, N] - x2_ref[t + N])**2 + \
            1.0 * (objective[:, N]**2)

    # Define the optimization problem
    problem = cp.Problem(cp.Minimize(cost), constraints)

    # Solve the problem
    problem.solve()

    # Extract the first control input and apply it
    u1_opt = u1.value[:, 0]
    u2_opt = u2.value[:, 0]
    u1_history.append(u1_opt)
    u2_history.append(u2_opt)

    # Simulate the system to get the next state
    x1_next = a1 * x1_history[-1] + a2 * x2_history[-1] + b1 * u1_opt + b2 * u2_opt
    x2_next = c1 * x1_history[-1] + c2 * x2_history[-1] + d1 * u1_opt + d2 * u2_opt
    x1_history.append(x1_next)
    x2_history.append(x2_next)

    # Update the objective variable
    objective_next = 0.9 * objective_history[-1] + 0.1 * (x1_history[-1] + x2_history[-1] + u1_opt + u2_opt)
    objective_history.append(objective_next)

# Convert lists to arrays for plotting
x1_history = np.array(x1_history).flatten()
x2_history = np.array(x2_history).flatten()
u1_history = np.array(u1_history).flatten()
u2_history = np.array(u2_history).flatten()
objective_history = np.array(objective_history).flatten()

# Plot the results
#st.header("Simulation Results")

# State trajectories
st.subheader("State Trajectories")
fig1, ax1 = plt.subplots()
ax1.plot(x1_history, label='State x1')
#ax1.plot(x1_ref[:sim_steps + 1], 'r--', label='Reference x1')
ax1.axhline(x1_min, color='r', linestyle='--', label='x1_min')
ax1.axhline(x1_max, color='r', linestyle='--', label='x1_max')
ax1.set_xlabel('Time step')
ax1.set_ylabel('State x1')
ax1.legend()
st.pyplot(fig1)

fig2, ax2 = plt.subplots()
ax2.plot(x2_history, label='State x2')
#ax2.plot(x2_ref[:sim_steps + 1], 'r--', label='Reference x2')
ax2.axhline(x2_min, color='r', linestyle='--', label='x2_min')
ax2.axhline(x2_max, color='r', linestyle='--', label='x2_max')
ax2.set_xlabel('Time step')
ax2.set_ylabel('State x2')
ax2.legend()
st.pyplot(fig2)

# Control inputs
st.subheader("Control Inputs")
fig3, ax3 = plt.subplots()
ax3.step(range(sim_steps), u1_history, label='Control Input u1')
ax3.axhline(u1_min, color='r', linestyle='--', label='u1_min')
ax3.axhline(u1_max, color='r', linestyle='--', label='u1_max')
ax3.set_xlabel('Time step')
ax3.set_ylabel('Control Input u1')
ax3.legend()
st.pyplot(fig3)

fig4, ax4 = plt.subplots()
ax4.step(range(sim_steps), u2_history, label='Control Input u2')
ax4.axhline(u2_min, color='r', linestyle='--', label='u2_min')
ax4.axhline(u2_max, color='r', linestyle='--', label='u2_max')
ax4.set_xlabel('Time step')
ax4.set_ylabel('Control Input u2')
ax4.legend()
st.pyplot(fig4)

# Objective variable
st.subheader("Objective Variable")
fig5, ax5 = plt.subplots()
ax5.plot(objective_history, label='Objective Variable')
ax5.set_xlabel('Time step')
ax5.set_ylabel('Objective Value')
ax5.legend()
st.pyplot(fig5)