# Frequency-Domain Analysis of Stock Returns

This project treats daily SPY log returns as a discrete-time signal and studies how that signal is represented across Fourier time scales.

The main pipeline is:

**returns → FFT → frequency bands → inverse FFT → reconstructed time-scale components**

The goal is not forecasting. The goal is to make the Fourier decomposition of a real financial signal visible and interpretable.

---

# Results

## 1. Fourier strength across time scales

The FFT represents the return signal using Fourier directions with different frequencies.

For each Fourier coefficient $X[k]$, define the normalized squared magnitude

$$
p_k =
\frac{|X[k]|^2}
{\sum_j |X[j]|^2}.
$$

The figure plots $100p_k$.

Therefore, if a Fourier bin has height

$$
100p_k = 4,
$$

then approximately **4% of the total squared magnitude of the retained one-sided Fourier coefficients** is associated with that bin.

![Normalized Fourier strength by period](figures/01_power_spectrum.png)

Rather than plotting the bin number $k$, the horizontal axis uses its corresponding period

$$
T_k = \frac{N}{k}
$$

in trading days.

The Fourier coefficients are divided into three illustrative time scales:

| Component | Period |
|---|---:|
| High frequency | $2 \le T \le 10$ trading days |
| Mid frequency | $10 < T \le 60$ trading days |
| Low frequency | $T > 60$ trading days |

The 60-day threshold is approximately a three-month trading horizon.  
The 10-day threshold is an illustrative short-horizon boundary.

These boundaries are chosen for interpretation rather than estimated from the data.

---

## 2. Progressive Fourier reconstruction

After separating the Fourier coefficients into frequency bands, each group can be transformed back into the time domain.

![Progressive Fourier reconstruction](figures/02_progressive_reconstruction.png)

The three panels progressively reconstruct the signal:

$$
x_{\text{low}}
$$

then

$$
x_{\text{low}} + x_{\text{mid}}
$$

and finally

$$
x_{\text{low}}
+
x_{\text{mid}}
+
x_{\text{high}}
=
x.
$$

The final reconstruction overlaps the original demeaned daily return signal.

Numerically,

$$
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
4.2 \times 10^{-17}.
$$

So the original demeaned return signal is recovered to floating-point precision.

The low-, mid-, and high-frequency curves are therefore not unrelated smoothers. They are different groups of coordinates from the **same Fourier representation**.

---

## 3. Cumulative contribution of the frequency bands

Daily returns are noisy, so the different time scales become easier to interpret after cumulative summation.

![Cumulative Fourier reconstruction](figures/03_cumulative_reconstruction.png)

The low-frequency component follows much of the broad shape of the cumulative demeaned return path.

The intuition is simple: high-frequency components oscillate rapidly and frequently change sign. When accumulated over longer intervals, many of these positive and negative movements cancel.

Low-frequency components persist for longer horizons, so they contribute more strongly to the broad cumulative shape.

These curves are cumulative **demeaned log returns**, not the actual SPY price path.

---

## 4. Fourier low-pass vs. causal filters

The Fourier low-frequency reconstruction keeps periods longer than 60 trading days.

Its cutoff angular frequency is

$$
\omega_c
=
\frac{2\pi}{60}
\approx
0.105
$$

radians per trading day.

To make the comparison with SMA and EMA meaningful, their parameters are chosen so that their gain is approximately

$$
\frac{1}{\sqrt{2}}
$$

at the same cutoff frequency.

This gives approximately

$$
M_{\text{SMA}} = 27
$$

and

$$
\alpha_{\text{EMA}} \approx 0.0993.
$$

![Fourier low-pass versus matched SMA and EMA](figures/04_filter_comparison.png)

The three methods isolate slower variation differently.

The Fourier mask has a sharp cutoff:

$$
|H(\omega)| =
\begin{cases}
1, & |\omega| < \omega_c, \\
0, & |\omega| > \omega_c.
\end{cases}
$$

The SMA has a smoother response with zeros and side lobes.

The EMA has a smooth monotonic roll-off.

There is also an important causality difference:

- the Fourier reconstruction uses the full sample and is therefore **offline / noncausal**;
- SMA and EMA use only present and past observations and are therefore **causal**.

Matching their cutoff frequencies does not make their outputs identical.

---

# Mathematics

## 1. Stock returns as a discrete-time signal

For adjusted closing price $P_t$, define the daily log return

$$
r_t =
\log P_t - \log P_{t-1}.
$$

Before applying the Fourier transform, remove the sample mean:

$$
x_t = r_t - \bar r.
$$

The analyzed signal is therefore the finite vector

$$
x =
\begin{bmatrix}
x_0 \\
x_1 \\
\vdots \\
x_{N-1}
\end{bmatrix}.
$$

---

## 2. DFT as a change of basis

The DFT can be viewed as a change of coordinates in linear algebra.

Instead of describing $x$ using the standard coordinate directions

$$
e_0,e_1,\ldots,e_{N-1},
$$

we describe it using Fourier directions.

Using the positive-sign convention used by Gilbert Strang, define

$$
w = e^{2\pi i/N}.
$$

Then

$$
w^N = 1.
$$

The numbers

$$
1,w,w^2,\ldots,w^{N-1}
$$

are the $N$-th roots of unity.

They lie equally spaced around the complex unit circle.

For example, if $N=8$,

$$
w = e^{2\pi i/8}.
$$

Multiplication by $w$ rotates a complex number by

$$
\frac{2\pi}{8}
$$

radians.

A Fourier mode with index $k$ uses the step

$$
w^k = e^{2\pi i k/N}.
$$

Its sequence is

$$
1,\;
w^k,\;
w^{2k},\;
w^{3k},
\ldots
$$

or as a vector,

$$
v_k =
\begin{bmatrix}
1 \\
w^k \\
w^{2k} \\
\vdots \\
w^{(N-1)k}
\end{bmatrix}.
$$

Larger $k$ generally corresponds to faster rotation around the unit circle and therefore a higher discrete frequency.

This is the geometric link between **roots of unity** and **frequency**.

---

## 3. Strang's Fourier convention

With

$$
w=e^{2\pi i/N},
$$

the positive-sign DFT is

$$
X[k]
=
\sum_{n=0}^{N-1}
x[n]w^{kn}.
$$

Equivalently,

$$
X[k]
=
\sum_{n=0}^{N-1}
x[n]e^{2\pi i kn/N}.
$$

The inverse transform is

$$
x[n]
=
\frac{1}{N}
\sum_{k=0}^{N-1}
X[k]w^{-kn}.
$$

NumPy uses the opposite sign for its forward FFT:

$$
X[k]
=
\sum_{n=0}^{N-1}
x[n]e^{-2\pi i kn/N}.
$$

This changes the orientation of the complex rotation, but not the quantities used in this project:

$$
|X[k]|
$$

and

$$
|X[k]|^2.
$$

Using NumPy's FFT and inverse FFT consistently reconstructs the same real-valued signal.

---

## 4. Fourier coefficients as alignment

Now connect the DFT directly to projection in linear algebra.

Normalize the Fourier direction:

$$
q_k[n]
=
\frac{1}{\sqrt{N}}w^{-kn}.
$$

Then

$$
\|q_k\| = 1.
$$

The normalized Fourier directions form an orthonormal basis.

The coordinate of the signal $x$ along direction $q_k$ is

$$
c_k
=
\langle q_k,x\rangle.
$$

For complex vectors,

$$
\langle q_k,x\rangle
=
q_k^*x.
$$

Under Strang's positive-sign convention,

$$
c_k
=
\frac{1}{\sqrt{N}}
\sum_{n=0}^{N-1}
x[n]w^{kn}.
$$

Therefore,

$$
X[k]
=
\sqrt{N}\,c_k.
$$

So, apart from the constant factor $\sqrt N$, the Fourier coefficient measures the **alignment of the signal with Fourier direction $k$**.

Large

$$
|X[k]|
$$

means strong alignment with that Fourier direction.

Small

$$
|X[k]|
$$

means weak alignment.

---

## 5. Why squared magnitude is called energy

For an orthonormal basis,

$$
x
=
\sum_k c_k q_k.
$$

Pythagoras gives

$$
\|x\|^2
=
\sum_k |c_k|^2.
$$

Since

$$
c_k
=
\frac{X[k]}{\sqrt N},
$$

we obtain Parseval's identity:

$$
\sum_{n=0}^{N-1}|x[n]|^2
=
\frac{1}{N}
\sum_{k=0}^{N-1}|X[k]|^2.
$$

This is the key reason for the signal-processing language.

The quantity

$$
|X[k]|^2
$$

is proportional to the squared length contributed by Fourier direction $k$.

A useful way to think about it is

$$
|X[k]|^2
\quad\approx\quad
\text{squared Fourier alignment}.
$$

The normalized quantity

$$
p_k
=
\frac{|X[k]|^2}
{\sum_j |X[j]|^2}
$$

therefore measures how much of the total squared Fourier magnitude is associated with bin $k$.

For example,

$$
p_k=0.04
$$

means that this bin contains approximately

$$
4\%
$$

of the normalized squared Fourier magnitude.

---

## 6. Why the code uses `rfft`

The return signal is real-valued.

For a real signal, the full DFT satisfies conjugate symmetry:

$$
X[N-k]
=
\overline{X[k]}.
$$

So the negative-frequency half contains no new information.

`np.fft.rfft` keeps only the nonnegative-frequency coefficients.

The plotted quantity

$$
p_k
=
\frac{|X[k]|^2}
{\sum_j|X[j]|^2}
$$

is normalized over these retained one-sided coefficients.

If an exact one-sided Parseval energy decomposition is required, the interior positive-frequency bins must be doubled to account for their omitted conjugate partners.

For this project, the normalized one-sided quantity is used primarily as an interpretable measure of Fourier strength across periods.

---

## 7. Frequency, bin, and period

For daily sampling, bin $k$ corresponds to frequency

$$
f_k
=
\frac{k}{N}
$$

cycles per trading day.

The angular frequency is

$$
\omega_k
=
\frac{2\pi k}{N}.
$$

The corresponding period is

$$
T_k
=
\frac{N}{k}
$$

trading days.

For example, if

$$
T_k=60,
$$

then the corresponding Fourier direction completes one cycle in approximately 60 trading observations.

This is why the figures use **period in trading days** rather than raw Fourier-bin number.

---

## 8. Frequency-domain masking

Once the signal has been transformed,

$$
x \longrightarrow X,
$$

the Fourier coordinates can be grouped by their periods.

For example,

$$
X^{\text{low}}[k]
=
\begin{cases}
X[k], & T_k>60, \\
0, & \text{otherwise}.
\end{cases}
$$

Similarly, $X^{\text{mid}}$ keeps periods between 10 and 60 trading days, while $X^{\text{high}}$ keeps periods between 2 and 10 days.

Because these masks partition the retained Fourier coefficients,

$$
X
=
X^{\text{low}}
+
X^{\text{mid}}
+
X^{\text{high}}.
$$

The inverse Fourier transform is linear, so

$$
x
=
x^{\text{low}}
+
x^{\text{mid}}
+
x^{\text{high}}.
$$

This explains why the numerical reconstruction error is essentially zero.

---

## 9. SMA as a FIR filter

A simple moving average is a finite impulse response filter:

$$
y_t
=
\frac{1}{M}
\sum_{j=0}^{M-1}x_{t-j}.
$$

Its impulse response is

$$
h[j]
=
\frac{1}{M},
\qquad
j=0,\ldots,M-1.
$$

Its frequency response is

$$
H_{\text{SMA}}(\omega)
=
\frac{1}{M}
\sum_{j=0}^{M-1}
e^{i\omega j}.
$$

Because the impulse response has only $M$ nonzero terms, the SMA is a **finite impulse response (FIR)** filter.

---

## 10. EMA as an IIR filter

The EMA satisfies

$$
y_t
=
\alpha x_t
+
(1-\alpha)y_{t-1}.
$$

Expanding recursively gives

$$
y_t
=
\alpha x_t
+
\alpha(1-\alpha)x_{t-1}
+
\alpha(1-\alpha)^2x_{t-2}
+
\cdots.
$$

Therefore its impulse response is

$$
h[n]
=
\alpha(1-\alpha)^n.
$$

The weights continue indefinitely, so EMA is an **infinite impulse response (IIR)** filter.

Its frequency response is

$$
H_{\text{EMA}}(\omega)
=
\frac{\alpha}
{1-(1-\alpha)e^{i\omega}}.
$$

Unlike the sharp Fourier mask, the EMA response decreases smoothly as frequency increases.

---

# Main takeaways

This project demonstrates several Signals & Systems ideas using a financial time series:

1. **DFT as a change of basis**  
   Returns are represented using Fourier directions instead of standard time-domain coordinates.

2. **Roots of unity as discrete frequencies**  
   Fourier basis vectors arise from equally spaced rotations around the complex unit circle.

3. **Fourier coefficients as projections**  
   $X[k]$ measures alignment with a particular Fourier direction.

4. **Squared coefficients as energy**  
   $|X[k]|^2$ is proportional to squared alignment, and Parseval connects these values to the norm of the original signal.

5. **Frequency-domain masking**  
   Fourier coordinates can be grouped by their corresponding time scales.

6. **Inverse reconstruction**  
   The selected bands transform back into time-domain signals that reconstruct the original demeaned returns.

7. **Offline Fourier filtering vs. causal filtering**  
   FFT masking gives sharp frequency separation using the full sample, while SMA and EMA operate causally with smoother frequency responses and lag.

The project studies signal decomposition rather than prediction or trading alpha.

---

# Limitations

- The full-sample FFT is retrospective and uses future observations relative to historical dates.
- A finite DFT implicitly assumes periodic extension of the observed sample.
- Sharp frequency masks can create ringing and endpoint effects.
- The 10-day and 60-day boundaries are illustrative rather than estimated.
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

Core numerical steps:

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