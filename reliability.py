import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# USER INPUTS
# -----------------------------
beta = 2.5                 # Weibull shape
eta_ref_hours = 20000.0    # Weibull scale in HOURS at reference condition (AF=1)

# Arrhenius AF assumptions (only needed if you don't already have AF per hour)
Tref_C = 25.0
Ea_J_per_mol = 80000.0
Rg = 8.314

# Choose constant-temperature comparison baseline:
# option 1: use mean of observed temps
use_mean_temp_as_constant = True
Tconst_C_manual = 40.0     # used only if use_mean_temp_as_constant=False

# Data file: timestamp,temp_C (hourly)
csv_path = Path("/mnt/data/temperature_hourly.csv")

# -----------------------------
# Load temperature data (or demo)
# -----------------------------
if csv_path.exists():
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
else:
    rng = pd.date_range("2026-01-01", periods=30*24, freq="h")
    base = 35 + 10*np.sin(2*np.pi*(np.arange(len(rng))/24.0))
    spikes = np.zeros(len(rng))
    spike_idx = np.random.default_rng(0).choice(len(rng), size=10, replace=False)
    spikes[spike_idx] = np.random.default_rng(1).uniform(10, 25, size=len(spike_idx))
    noise = np.random.default_rng(2).normal(0, 1.2, size=len(rng))
    df = pd.DataFrame({"timestamp": rng, "temp_C": base + spikes + noise})

# dt in hours (handles minor irregularities)
df["dt_hours"] = df["timestamp"].diff().dt.total_seconds().div(3600.0)
df.loc[df["dt_hours"].isna(), "dt_hours"] = 0.0

# elapsed calendar time in hours since start (for plotting against "time")
df["t_hours"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds() / 3600.0

# -----------------------------
# Compute AF(T) from Arrhenius
# AF(Tref)=1 by construction
# -----------------------------
Tref_K = Tref_C + 273.15
df["T_K"] = df["temp_C"] + 273.15
df["AF"] = np.exp((Ea_J_per_mol / Rg) * (1.0 / Tref_K - 1.0 / df["T_K"]))

# -----------------------------
# Case A: fluctuating temperature -> effective age u_fluc(t)
# -----------------------------
df["u_fluc_hours"] = (df["AF"] * df["dt_hours"]).cumsum()

# -----------------------------
# Case B: constant temperature -> u_const(t) = AF(Tconst) * t
# -----------------------------
if use_mean_temp_as_constant:
    Tconst_C = df["temp_C"].mean()
else:
    Tconst_C = Tconst_C_manual

Tconst_K = Tconst_C + 273.15
AF_const = np.exp((Ea_J_per_mol / Rg) * (1.0 / Tref_K - 1.0 / Tconst_K))

df["u_const_hours"] = AF_const * df["t_hours"]

# -----------------------------
# Weibull CDF for both cases: F = 1 - exp(-(u/eta)^beta)
# -----------------------------
eta = eta_ref_hours

df["F_fluc"]  = 1.0 - np.exp(- (df["u_fluc_hours"]  / eta) ** beta)
df["F_const"] = 1.0 - np.exp(- (df["u_const_hours"] / eta) ** beta)

# (optional) PDF in calendar-time, if you want it:
# f(t) = dF/dt. We'll approximate by finite differences.
df["f_fluc"]  = df["F_fluc"].diff() / df["dt_hours"]
df["f_const"] = df["F_const"].diff() / df["dt_hours"]

# -----------------------------
# PLOT 1: Temperature time series
# -----------------------------
plt.figure()
plt.plot(df["timestamp"], df["temp_C"])
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.title("Hourly Temperature (Observed)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig("temp_timeseries.png")
plt.close()

# -----------------------------
# PLOT 2: CDF comparison (probability of failure by time t)
# -----------------------------
plt.figure()
plt.plot(df["timestamp"], df["F_const"], label=f"Constant T = {Tconst_C:.2f}°C")
plt.plot(df["timestamp"], df["F_fluc"],  label="Fluctuating T (history-aware)")
plt.xlabel("Time")
plt.ylabel("Probability of Failure by time t  (CDF)  F(t)")
plt.title("Weibull Failure Probability: Constant vs Fluctuating Temperature")
plt.xticks(rotation=30)
plt.legend()
plt.tight_layout()
plt.savefig("cdf_comparison.png")
plt.close()

# -----------------------------
# OPTIONAL PLOT 3: PDF comparison (density per hour)
# -----------------------------
plt.figure()
plt.plot(df["timestamp"], df["f_const"], label="PDF (constant T)")
plt.plot(df["timestamp"], df["f_fluc"],  label="PDF (fluctuating T)")
plt.xlabel("Time")
plt.ylabel("Failure density per hour  f(t)")
plt.title("Optional: Failure PDF (finite-difference approximation)")
plt.xticks(rotation=30)
plt.legend()
plt.tight_layout()
plt.savefig("pdf_comparison.png")
plt.close()

print("Constant-temperature baseline used:", Tconst_C, "°C")
print("AF_const:", AF_const)
print(df[["timestamp","temp_C","AF","u_const_hours","u_fluc_hours","F_const","F_fluc"]].head(10))
