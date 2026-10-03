# Frequency-Domain Analysis of Stock Returns

This project treats daily SPY log returns as a discrete-time signal and studies how that signal can be decomposed across different Fourier time scales.

The main pipeline is:

**returns → FFT → frequency bands → inverse FFT → reconstructed time-scale components**

The project focuses on signal decomposition rather than forecasting or trading alpha.

---

# Results

## 1. Progressive Fourier reconstruction

The main result is easiest to see directly in the time domain.

The Fourier coefficients are separated into three groups:

- low frequency: periods longer than 60 trading days,
- mid frequency: periods between 10 and 60 trading days,
- high frequency: periods between 2 and 10 trading days.

Each group is transformed back into the time domain with the inverse FFT.

![Progressive Fourier reconstruction](figures/02_progressive_reconstruction.png)

The three panels progressively add frequency ranges:

```math
x_{\text{low}}
```

then

```math
x_{\text{low}} + x_{\text{mid}}
```

and finally

```math
x_{\text{low}}
+
x_{\text{mid}}
+
x_{\text{high}}
=
x.
```

The final reconstruction overlaps the original demeaned daily return signal.

Numerically,

```math
\max_t
\left|
x_t -
\left(
x_t^{\text{low}}
+
x_t^{\text{mid}}
+
x_t^{\text{high}}
\right)
\right|
\approx
4.2\times10^{-17}.
```

So the original signal is recovered to floating-point precision.

The important point is that these are not three unrelated smoothers. They are three groups of coordinates from the **same Fourier representation**.

---

## 2. Cumulative contribution of the frequency bands

Daily returns are noisy, so the decomposition becomes easier to interpret after cumulative summation.

![Cumulative Fourier reconstruction](figures/03_cumulative_reconstruction.png)

The low-frequency component follows much of the broad shape of the cumulative demeaned return path.

The intuition is simple:

high-frequency components change sign rapidly, so many positive and negative movements cancel when accumulated over longer intervals.

Low-frequency components vary more slowly, so their contribution persists over longer horizons.

These curves are cumulative **demeaned log returns**, not the actual SPY price path.

---

## 3. Fourier low-pass vs. causal SMA and EMA filters

The Fourier low-frequency component keeps periods longer than 60 trading days.

Its cutoff angular frequency is

```math
\omega_c
=
\frac{2\pi}{60}
\approx
0.105
```

radians per trading day.

To make the comparison with SMA and EMA meaningful, their parameters are chosen so that their gain is approximately

```math
\frac{1}{\sqrt{2}}
```

at the same cutoff frequency.

This gives approximately

```math
M_{\text{SMA}}=27
```

and

```math
\alpha_{\text{EMA}}\approx0.0993.
```

![Fourier low-pass versus matched SMA and EMA](figures/04_filter_comparison.png)

The filters have similar cutoff frequencies but very different behavior.

The Fourier mask has a sharp cutoff:

```math
|H(\omega)|
=
\begin{cases}
1, & |\omega|<\omega_c,\\
0, & |\omega|>\omega_c.
\end{cases}
```

The SMA has a smoother response with zeros and side lobes.

The EMA has a smooth monotonic roll-off.

There is also an important causality difference:

- the Fourier reconstruction uses the entire sample and is therefore **offline / noncausal**;
- SMA and EMA use only current and past observations and are therefore **causal**.

The causal filters therefore show lag relative to the full-sample Fourier reconstruction.

---

# Mathematics

## 1. Stock returns as a discrete-time signal

For adjusted closing price $P_t$, define the daily log return

```math
r_t
=
\log P_t-\log P_{t-1}.
```

Before applying the Fourier transform, remove the sample mean:

```math
x_t=r_t-\bar r.
```

The analyzed signal is therefore

```math
x=
\begin{bmatrix}
x_0\\
x_1\\
\vdots\\
x_{N-1}
\end{bmatrix}.
```

The mean removal also removes the zero-frequency or **DC component**.

---

## 2. DFT as a change of basis

The DFT can be interpreted as a change of coordinates in linear algebra.

In the standard basis, a vector is described using

```math
e_0,e_1,\ldots,e_{N-1}.
```

The Fourier transform instead describes the same vector using oscillating complex basis directions.

Following the positive-sign convention used by Gilbert Strang, define

```math
w=e^{2\pi i/N}.
```

Since

```math
w^N=e^{2\pi i}=1,
```

the numbers

```math
1,w,w^2,\ldots,w^{N-1}
```

are the $N$-th roots of unity.

They are equally spaced around the complex unit circle.

---

## 3. Roots of unity and the complex circle

For example, if $N=8$,

```math
w=e^{2\pi i/8}.
```

Multiplying by $w$ rotates a point around the unit circle by

```math
\frac{2\pi}{8}
```

radians.

A Fourier mode with index $k$ uses the step

```math
w^k=e^{2\pi i k/N}.
```

Its sequence is

```math
1,\;
w^k,\;
w^{2k},\;
w^{3k},
\ldots
```

and the corresponding Fourier direction is

```math
v_k=
\begin{bmatrix}
1\\
w^k\\
w^{2k}\\
\vdots\\
w^{(N-1)k}
\end{bmatrix}.
```

So a Fourier mode can be interpreted geometrically as repeatedly rotating around the complex unit circle.

For $k=0$,

```math
w^0=1,
```

so there is no rotation. This is the constant or DC component.

For $k=1$, the rotation is slow.

As $k$ increases, the rotation becomes faster, corresponding to higher discrete frequencies.

This is the geometric connection

**roots of unity → rotation → discrete frequency**.

---

## 4. Strang's Fourier convention

Using

```math
w=e^{2\pi i/N},
```

Strang's positive-sign DFT is

```math
X[k]
=
\sum_{n=0}^{N-1}
x[n]w^{kn}.
```

Equivalently,

```math
X[k]
=
\sum_{n=0}^{N-1}
x[n]e^{2\pi i kn/N}.
```

The inverse transform uses the opposite sign:

```math
x[n]
=
\frac{1}{N}
\sum_{k=0}^{N-1}
X[k]w^{-kn}.
```

NumPy uses the opposite sign convention for the forward FFT:

```math
X[k]
=
\sum_{n=0}^{N-1}
x[n]e^{-2\pi i kn/N}.
```

This reverses the direction of rotation around the complex circle.

However, the quantities used in this project,

```math
|X[k]|
```

and

```math
|X[k]|^2,
```

are unchanged.

Using NumPy's FFT and inverse FFT consistently therefore gives the same real-valued reconstruction.

---

## 5. Fourier coefficients as alignment

To connect the DFT directly to projection in linear algebra, normalize the Fourier direction:

```math
q_k[n]
=
\frac{1}{\sqrt{N}}w^{-kn}.
```

Then

```math
\|q_k\|=1.
```

The Fourier directions form an orthonormal basis.

The coordinate of the signal $x$ along direction $q_k$ is its projection:

```math
c_k
=
\langle q_k,x\rangle.
```

For complex vectors,

```math
\langle q_k,x\rangle
=
q_k^*x.
```

Substituting the Fourier direction gives

```math
c_k
=
\frac{1}{\sqrt{N}}
\sum_{n=0}^{N-1}
x[n]w^{kn}.
```

Therefore, under Strang's convention,

```math
X[k]
=
\sqrt{N}\,c_k.
```

So the Fourier coefficient is, up to the constant factor $\sqrt N$, a measure of the **alignment of the signal with Fourier direction $k$**.

A large value of

```math
|X[k]|
```

means that the signal has a strong component in Fourier direction $k$.

A small value means weak alignment with that direction.

---

## 6. From alignment to energy

Because the normalized Fourier directions form an orthonormal basis,

```math
x
=
\sum_k c_k q_k.
```

Pythagoras gives

```math
\|x\|^2
=
\sum_k |c_k|^2.
```

Since

```math
X[k]
=
\sqrt{N}\,c_k,
```

we obtain Parseval's identity:

```math
\sum_{n=0}^{N-1}|x[n]|^2
=
\frac{1}{N}
\sum_{k=0}^{N-1}|X[k]|^2.
```

This explains the signal-processing term **energy**.

The quantity

```math
|X[k]|^2
```

is proportional to the squared contribution of Fourier direction $k$.

A useful mental model is

```math
|X[k]|^2
\quad\longleftrightarrow\quad
\text{squared alignment with Fourier direction }k.
```

The normalized quantity used in the project is

```math
p_k
=
\frac{|X[k]|^2}
{\sum_j |X[j]|^2}.
```

This tells us how much of the total squared Fourier magnitude is associated with one retained Fourier bin.

For example, if the plotted value is

```math
100p_k=0.6,
```

then that bin contains approximately **0.6% of the normalized squared magnitude of the retained one-sided Fourier coefficients**.

---

## 7. Fourier strength across time scales

Now the normalized Fourier-strength plot has a direct interpretation.

![Normalized Fourier strength by period](figures/01_power_spectrum.png)

The vertical axis shows

```math
100p_k
=
100
\frac{|X[k]|^2}
{\sum_j|X[j]|^2}.
```

The horizontal axis does not show raw Fourier-bin number. Instead it shows the corresponding period in trading days.

For a sample of length $N$,

```math
f_k=\frac{k}{N}
```

cycles per trading day.

The angular frequency is

```math
\omega_k
=
\frac{2\pi k}{N}.
```

The corresponding period is

```math
T_k
=
\frac{N}{k}.
```

So a Fourier bin with

```math
T_k=60
```

represents an oscillation that completes one cycle in approximately 60 trading observations.

The frequency bands used in the project are:

| Component | Period |
|---|---:|
| High frequency | $2 \le T \le 10$ trading days |
| Mid frequency | $10 < T \le 60$ trading days |
| Low frequency | $T > 60$ trading days |

The 60-day boundary is approximately a three-month trading horizon.

The 10-day boundary is an illustrative short-horizon cutoff.

These values are chosen for interpretation rather than estimated from the data.

---

## 8. Why the code uses `rfft`

The SPY return signal is real-valued.

For a real signal, the full DFT has conjugate symmetry:

```math
X[N-k]
=
\overline{X[k]}.
```

So the negative-frequency coefficients contain the same magnitude information as their positive-frequency partners.

`np.fft.rfft` therefore keeps only the nonnegative-frequency half.

The project plots

```math
p_k
=
\frac{|X[k]|^2}
{\sum_j|X[j]|^2}
```

over these retained one-sided coefficients.

This is useful for comparing Fourier strength across periods.

For an exact one-sided Parseval energy decomposition, the interior positive-frequency bins would need to be doubled to account for their omitted conjugate partners.

---

## 9. Frequency-domain masking

Once the signal has been transformed,

```math
x
\longrightarrow
X,
```

we can select groups of Fourier coordinates.

For the low-frequency component,

```math
X^{\text{low}}[k]
=
\begin{cases}
X[k], & T_k>60,\\
0, & \text{otherwise}.
\end{cases}
```

Similarly, $X^{\text{mid}}$ keeps periods between 10 and 60 trading days, while $X^{\text{high}}$ keeps periods between 2 and 10 trading days.

The masks partition the retained Fourier coefficients:

```math
X
=
X^{\text{low}}
+
X^{\text{mid}}
+
X^{\text{high}}.
```

Because the inverse Fourier transform is linear,

```math
x
=
x^{\text{low}}
+
x^{\text{mid}}
+
x^{\text{high}}.
```

This is why the original return signal can be reconstructed to machine precision.

---

## 10. SMA as a FIR filter

A simple moving average is

```math
y_t
=
\frac{1}{M}
\sum_{j=0}^{M-1}x_{t-j}.
```

Its impulse response is

```math
h[j]
=
\frac{1}{M},
\qquad
j=0,\ldots,M-1.
```

Only a finite number of past observations have nonzero weights, so SMA is a **finite impulse response (FIR)** filter.

Its frequency response is

```math
H_{\text{SMA}}(\omega)
=
\frac{1}{M}
\sum_{j=0}^{M-1}
e^{i\omega j}.
```

This produces the characteristic zeros and side lobes visible in the filter-response figure.

---

## 11. EMA as an IIR filter

The exponential moving average satisfies

```math
y_t
=
\alpha x_t
+
(1-\alpha)y_{t-1}.
```

Expanding the recursion gives

```math
y_t
=
\alpha x_t
+
\alpha(1-\alpha)x_{t-1}
+
\alpha(1-\alpha)^2x_{t-2}
+
\cdots.
```

Therefore its impulse response is

```math
h[n]
=
\alpha(1-\alpha)^n.
```

The weights continue indefinitely, so EMA is an **infinite impulse response (IIR)** filter.

Its frequency response is

```math
H_{\text{EMA}}(\omega)
=
\frac{\alpha}
{1-(1-\alpha)e^{i\omega}}.
```

Unlike the sharp Fourier mask, the EMA response decreases smoothly as frequency increases.

---

# Main takeaways

1. **DFT is a change of basis.**  
   The same return signal can be described using Fourier coordinates instead of standard time-domain coordinates.

2. **Roots of unity generate discrete frequencies.**  
   Fourier directions correspond to repeated rotations around the complex unit circle.

3. **Fourier coefficients measure alignment.**  
   $X[k]$ is proportional to the projection of the signal onto Fourier direction $k$.

4. **Squared Fourier coefficients measure energy.**  
   $|X[k]|^2$ is proportional to squared alignment, and Parseval connects these quantities to the norm of the original signal.

5. **Frequency bands can be reconstructed.**  
   Selecting Fourier coordinates and applying the inverse FFT produces low-, mid-, and high-frequency time-domain components.

6. **The original signal is recovered exactly.**  
   Adding those components reconstructs the demeaned return series to floating-point precision.

7. **Fourier filtering and causal filtering are different.**  
   A full-sample FFT gives sharp offline frequency separation, while SMA and EMA operate causally with smoother frequency responses and lag.

The project studies signal decomposition, not forecasting or trading alpha.

---

# Limitations

- The full-sample FFT is retrospective and uses the complete observed sample.
- A finite DFT implicitly treats the observed signal as periodically extended.
- Sharp frequency masks can create ringing and endpoint effects.
- The 10-day and 60-day boundaries are illustrative.
- Frequency decomposition alone does not imply predictability.

---

# Repository

```text
frequency-domain-analysis/
├── README.md
├── requirements.txt
├── data/
├── figures/
├── notebooks/
│   ├── 01_fft_decomposition.ipynb
│   └── 02_filter_comparison.ipynb
├── scripts/
└── src/
    ├── data.py
    ├── fourier.py
    └── filters.py
```

The core numerical operations remain explicit:

```python
x = returns - returns.mean()

X = np.fft.rfft(x)

power = np.abs(X) ** 2
p = power / power.sum()

X_low = np.where(low_mask, X, 0)
x_low = np.fft.irfft(X_low, n=len(x))
```

---

# Run

Install the dependencies from `requirements.txt`, then execute the notebooks or run:

```bash
python scripts/run_notebooks.py
```