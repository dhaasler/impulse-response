# region LEVEL 0: imports and aux functions
# -------- 0 imports and aux functions -------- #

import marimo as mo
import matplotlib.pyplot as plt
import numpy as np

def gaussian_profile(x, x0, sigma, amp):
    return amp * np.exp(-(x - x0)**2 / (2 * sigma**2))

# endregion (End 0)


# region LEVEL 1: User input
# -------- 1 User input -------- #

# np.random.seed(4)

# Create a velocity axis
n_chan = 2000
vel = np.linspace(-10, 10, n_chan)  # km/s

# Line parameters (velocity [km/s], width [km/s], peak intensity)
true_vel = 1
lines = [
    (true_vel + 0.0, 0.05, 1.0),
    (true_vel + 0.15, 0.05, 0.5),
    (true_vel - 0.15, 0.05, 0.3),
]

figsize = (10, 5.4)

# endregion (End 1)


# region LEVEL 2: Create model and simulated noisy data
# -------- 2 Create model and simulated noisy data -------- #

# Channel width
dv = vel[1] - vel[0]

# Create model
model = np.zeros_like(vel)
for v0, sigma, amp in lines:
    model += gaussian_profile(vel, v0, sigma, amp)

# Get velocity of first line
first_vel = lines[0][0]

# Normalize the model
model /= np.sqrt(np.sum(model**2))

# Create noisy observed data
noise_rms = 0.1
noise = np.random.normal(0.0, noise_rms, n_chan)

simulated_data = model + noise

# endregion (End 2)


# region LEVEL 3: Compute cross-correlation
# -------- 3 Compute cross-correlation -------- #

## >> Numpy cross-correlation
corr_np = np.correlate(simulated_data, model, mode='same')

# Normalize correlation to S/N units
corr_np /= np.std(corr_np)
# corr_np /= (np.std(corr_np)**2)

# Compute lag axis
lags = (np.arange(n_chan) - n_chan//2) * dv


## >> Scipy FFT cross-correlation

F_data = np.fft.fft(simulated_data)
F_model = np.fft.fft(model)
corr_fft = np.fft.ifft(F_data * np.conj(F_model)).real
# Move zero lag to the center
corr_fft = np.fft.fftshift(corr_fft)
corr_fft /= np.std(corr_fft)

# endregion (End 3)


# region LEVEL 4: Show results
# -------- 4 Show results -------- #

fig, axes = plt.subplots(4, 1, figsize=figsize, sharex=True)

axes[0].plot(vel, model, color="red")
axes[0].set_ylabel("Model")
axes[0].set_title("Model molecular emission")

axes[1].plot(vel, simulated_data, label="Simulated data",
             color="black", alpha=0.8)
axes[1].plot(vel, model, color="red", label="True model")
# axes[1].axvline(0.0, color="k", ls="--", alpha=0.5)
axes[1].set_ylabel("Intensity")
axes[1].set_title("Noisy spectrum with true signal location")
axes[1].set_xlabel("Velocity [km/s]")

# Old plotting velocity and corr (incorrect, I needed to
# compute the lag axis)
# axes[2].plot(vel, corr_np)
axes[2].plot(lags, corr_np)
axes[2].set_ylabel("Correlation (S/N)")
axes[2].set_title("Numpy Cross-correlation")

axes[3].plot(lags, corr_fft)
axes[3].set_xlabel("Velocity shift (km/s)")
axes[3].set_ylabel("Correlation")
axes[3].set_title("Scipy FFT Cross-correlation")

peak_sn = np.max(corr_np)
peak_shift = lags[np.argmax(corr_np)]
peak_vel = peak_shift + first_vel

print(f"Peak correlation S/N            = {peak_sn:.2f}")
print(f"Recovered shift                 = {peak_shift:.3f} km/s")
print(f"Detected velocity of first comp = {peak_vel:.3f} km/s")
print(f"True velocity of signal         = {true_vel:.3f} km/s")

plt.tight_layout()
plt.show()

# endregion (End 4)
