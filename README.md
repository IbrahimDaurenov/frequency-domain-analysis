# Frequency-Domain Analysis of Stock Returns

This project treats daily SPY log returns as a discrete-time signal and studies how that signal is represented across Fourier time scales.

The main pipeline is

\[
\boxed{
\text{returns}
\rightarrow
\text{FFT}
\rightarrow
\text{frequency bands}
\rightarrow
\text{inverse FFT}
\rightarrow
\text{time-domain components}
}
\]

The goal is not forecasting. The goal is to make the Fourier decomposition of a real financial signal visible and interpretable.

---

# Results

## 1. Fourier strength across time scales

The FFT represents the return signal using Fourier directions with different frequencies.

For each Fourier coefficient \(X[k]\), the plotted quantity is its normalized squared magnitude,

\[
p_k
=
\frac{|X[k]|^2}
{\sum_j |X[j]|^2}.
\]

The figure plots \(100p_k\), so a value of \(4\) means that approximately \(4\%\) of the total squared magnitude of the retained one-sided Fourier coefficients is associated with that bin.

![Normalized Fourier strength by period](figures/01_power_spectrum.png)

Rather than plotting bin number \(k\), the horizontal axis uses the corresponding period

\[
T_k = \frac{N}{k}
\]

in trading days.

The shaded regions divide the return signal into three illustrative time scales:

| Component | Period |
|---|---:|
| High frequency | \(2 \le T \le 10\) trading days |
| Mid frequency | \(10 < T \le 60\) trading days |
| Low frequency | \(T > 60\) trading days |

The 60-day threshold is approximately a three-month trading horizon.  
The 10-day threshold is an illustrative short-horizon boundary.

These thresholds are chosen for interpretation; they are not estimated from the data.

---

## 2. Progressive Fourier reconstruction

After splitting the Fourier coefficients into frequency bands, each band can be transformed back into the time domain.

![Progressive Fourier reconstruction](figures/02_progressive_reconstruction.png)

The three panels progressively add Fourier components:

\[
x_{\text{low}}
\]

then

\[
x_{\text{low}} + x_{\text{mid}}
\]

and finally

\[
x_{\text{low}}
+
x_{\text{mid}}
+
x_{\text{high}}
=
x.
\]

The final reconstructed signal overlaps the original demeaned daily return signal.

Numerically,

\[
\max_t
\left|
x_t -
\left(
x_t^{\text{low}}
+x_t^{\text{mid}}
+x_t^{\text{high}}
\right)
\right|
\approx
4.2\times10^{-17}.
\]

So the reconstruction is exact up to floating-point precision.

This is the central result of the project: the three curves are not unrelated smoothers. They are different groups of coordinates from the same Fourier representation.

---

## 3. Cumulative contribution of the frequency bands

Individual daily returns are noisy, so the different time scales become easier to see after cumulative summation.

![Cumulative Fourier reconstruction](figures/03_cumulative_reconstruction.png)

The low-frequency component follows much of the broad shape of the cumulative demeaned return signal.

This has a simple interpretation.

High-frequency components oscillate rapidly and repeatedly change sign, so positive and negative contributions often cancel when accumulated over long intervals.

Low-frequency components vary more slowly, so their contribution persists over longer horizons.

These curves are cumulative **demeaned log returns**, not the SPY price path.

---

## 4. Fourier low-pass vs. causal filters

The low-frequency Fourier component keeps periods longer than 60 trading days.

Its cutoff angular frequency is

\[
\omega_c
=
\frac{2\pi}{60}
\approx
0.105
\quad
\text{radians per trading day}.
\]

To compare this with time-domain filters, SMA and EMA parameters are chosen so that their gain is approximately

\[
\frac{1}{\sqrt 2}
\]

at the same cutoff frequency.

This gives approximately

\[
M_{\text{SMA}}=27
\]

and

\[
\alpha_{\text{EMA}}\approx0.0993.
\]

![Fourier low-pass versus matched SMA and EMA](figures/04_filter_comparison.png)

The three methods isolate slower variation differently.

The Fourier mask has an ideal sharp cutoff:

\[
|H(\omega)|
=
\begin{cases}
1, & |\omega|<\omega_c,\\
0, & |\omega|>\omega_c.
\end{cases}
\]

The SMA has a smoother response with zeros and side lobes.

The EMA has a smooth monotonic roll-off.

There is also a major causality difference:

- the Fourier reconstruction uses the full sample and is therefore **offline / noncausal**;
- SMA and EMA use only present and past observations and are therefore **causal**.

Matching their cutoff frequencies does not make their outputs identical.

---

# Mathematics

## 1. Stock returns as a discrete-time signal

For adjusted closing price \(P_t\),

\[
r_t
=
\log P_t-\log P_{t-1}.
\]

The sample mean is removed before applying the FFT:

\[
x_t=r_t-\bar r.
\]

Thus the object analyzed by the Fourier transform is the vector

\[
x=
\begin{bmatrix}
x_0\\
x_1\\
\vdots\\
x_{N-1}
\end{bmatrix}.
\]

This is a finite discrete-time signal of length \(N\).

---

## 2. DFT as a change of basis

The Fourier transform can be viewed exactly like a change of coordinates in linear algebra.

Instead of describing \(x\) using the standard coordinate directions

\[
e_0,e_1,\ldots,e_{N-1},
\]

we describe it using Fourier directions.

Using the positive-sign convention from Gilbert Strang, define

\[
\boxed{
w=e^{2\pi i/N}.
}
\]

Then

\[
w^N=1.
\]

The numbers

\[
1,w,w^2,\ldots,w^{N-1}
\]

are the \(N\)-th roots of unity.

They lie equally spaced around the complex unit circle.

For example, for \(N=8\),

\[
w=e^{2\pi i/8}.
\]

Each multiplication by \(w\) rotates a complex number by

\[
\frac{2\pi}{8}
\]

radians around the circle.

A Fourier mode with index \(k\) uses the step

\[
w^k=e^{2\pi i k/N}.
\]

Its sequence is

\[
1,\;
w^k,\;
w^{2k},\;
w^{3k},
\ldots
\]

or, as a vector,

\[
v_k=
\begin{bmatrix}
1\\
w^k\\
w^{2k}\\
\vdots\\
w^{(N-1)k}
\end{bmatrix}.
\]

Larger \(k\) generally means faster rotation around the unit circle and therefore a higher discrete frequency.

This is the geometric connection between the roots-of-unity circle and frequency.

---

## 3. Strang convention

With

\[
w=e^{2\pi i/N},
\]

the positive-sign DFT is

\[
\boxed{
X[k]
=
\sum_{n=0}^{N-1}
x[n]w^{kn}
}
\]

or equivalently

\[
X[k]
=
\sum_{n=0}^{N-1}
x[n]
e^{2\pi i kn/N}.
\]

The inverse transform uses the opposite sign:

\[
\boxed{
x[n]
=
\frac{1}{N}
\sum_{k=0}^{N-1}
X[k]w^{-kn}.
}
\]

NumPy uses the opposite sign convention for the forward FFT:

\[
e^{-2\pi i kn/N}.
\]

This only changes which member of each conjugate Fourier pair receives the positive-frequency label.

Magnitude,

\[
|X[k]|,
\]

squared magnitude,

\[
|X[k]|^2,
\]

and consistent FFT/IFFT reconstruction are unchanged.

---

## 4. Fourier coefficients as alignment

To connect the DFT directly to linear algebra, normalize the Fourier directions.

Define

\[
q_k[n]
=
\frac{1}{\sqrt N}w^{-kn}.
\]

Then

\[
\|q_k\|=1
\]

and the Fourier directions form an orthonormal basis.

The coordinate of \(x\) along direction \(q_k\) is its projection

\[
c_k
=
\langle q_k,x\rangle.
\]

Under the Strang convention,

\[
X[k]
=
\sqrt N\,c_k.
\]

Therefore the Fourier coefficient is, up to the constant factor \(\sqrt N\), the **alignment of the signal with Fourier direction \(k\)**.

If

\[
|X[k]|
\]

is large, then the signal has a strong component in that Fourier direction.

If it is small, the signal has little alignment with that direction.

---

## 5. Why squared magnitude is called energy

For an orthonormal basis,

\[
x
=
\sum_k c_k q_k.
\]

Pythagoras gives

\[
\boxed{
\|x\|^2
=
\sum_k |c_k|^2.
}
\]

Because

\[
c_k=\frac{X[k]}{\sqrt N},
\]

we obtain Parseval's identity for the unnormalized DFT:

\[
\boxed{
\sum_{n=0}^{N-1}|x[n]|^2
=
\frac{1}{N}
\sum_{k=0}^{N-1}|X[k]|^2.
}
\]

So

\[
|X[k]|^2
\]

is proportional to the squared length contributed by Fourier direction \(k\).

That is why signal processing calls it **energy** or **power**.

A useful mental model is

\[
\boxed{
|X[k]|^2
=
\text{squared Fourier alignment}.
}
\]

After normalization,

\[
p_k
=
\frac{|X[k]|^2}
{\sum_j |X[j]|^2},
\]

we obtain the fraction of total squared Fourier magnitude associated with bin \(k\).

So if

\[
p_k=0.04,
\]

that Fourier direction contributes about

\[
4\%
\]

of the normalized squared coefficient magnitude.

### Note on `rfft`

The code uses `np.fft.rfft` because the return signal is real-valued.

For a real signal,

\[
X[N-k]
=
\overline{X[k]}.
\]

Negative-frequency coefficients therefore contain no new information and `rfft` keeps only the nonnegative-frequency half.

The displayed normalized strength is normalized over these retained one-sided coefficients.

If exact Parseval energy shares are required in a one-sided representation, interior positive-frequency bins must be doubled to account for their omitted conjugate partners.

---

## 6. Frequency, period, and Fourier bin

For daily observations, Fourier bin \(k\) corresponds to

\[
f_k=\frac{k}{N}
\]

cycles per trading day.

Its angular frequency is

\[
\omega_k
=
\frac{2\pi k}{N}.
\]

The corresponding period is

\[
\boxed{
T_k=\frac{N}{k}
}
\]

trading days.

For example,

\[
T_k=60
\]

means that the Fourier direction completes one full complex rotation approximately every 60 trading observations.

This is why period is often easier to interpret than raw bin number.

---

## 7. Frequency-domain masking

Once the signal has been transformed,

\[
x
\rightarrow
X,
\]

the Fourier coordinates can be separated by period.

For example,

\[
X^{\text{low}}[k]
=
\begin{cases}
X[k], & T_k>60,\\
0, & \text{otherwise}.
\end{cases}
\]

Similarly,

\[
X^{\text{mid}}
\]

keeps only periods between 10 and 60 trading days, and

\[
X^{\text{high}}
\]

keeps periods between 2 and 10 trading days.

Because the masks partition the retained Fourier coordinates,

\[
X
=
X^{\text{low}}
+
X^{\text{mid}}
+
X^{\text{high}}.
\]

The inverse FFT is linear, so

\[
\operatorname{IFFT}(X)
=
\operatorname{IFFT}(X^{\text{low}})
+
\operatorname{IFFT}(X^{\text{mid}})
+
\operatorname{IFFT}(X^{\text{high}}).
\]

Therefore

\[
\boxed{
x
=
x^{\text{low}}
+
x^{\text{mid}}
+
x^{\text{high}}.
}
\]

This is why the reconstruction works to machine precision.

---

## 8. SMA as a FIR filter

A moving average is a finite impulse response filter:

\[
y_t
=
\frac{1}{M}
\sum_{j=0}^{M-1}x_{t-j}.
\]

Its impulse response is

\[
h[j]
=
\frac{1}{M},
\qquad
j=0,\ldots,M-1.
\]

Its frequency response is

\[
H_{\text{SMA}}(\omega)
=
\frac{1}{M}
\sum_{j=0}^{M-1}
e^{i\omega j}.
\]

The finite equal weights produce the oscillating magnitude response and its characteristic zeros and side lobes.

---

## 9. EMA as an IIR filter

The EMA obeys the recursion

\[
y_t
=
\alpha x_t
+
(1-\alpha)y_{t-1}.
\]

Expanding recursively,

\[
y_t
=
\alpha x_t
+
\alpha(1-\alpha)x_{t-1}
+
\alpha(1-\alpha)^2x_{t-2}
+\cdots
\]

so the impulse response is

\[
\boxed{
h[n]
=
\alpha(1-\alpha)^n.
}
\]

Because this sequence continues indefinitely, EMA is an infinite impulse response filter.

Its frequency response is

\[
H_{\text{EMA}}(\omega)
=
\frac{\alpha}
{1-(1-\alpha)e^{i\omega}}.
\]

Unlike the sharp Fourier mask, its magnitude decreases smoothly as frequency increases.

---

# Main takeaways

This project demonstrates several Signals & Systems ideas using a financial time series:

1. **DFT as a change of basis**  
   Returns are expressed using Fourier directions instead of time-domain coordinate directions.

2. **Roots of unity as discrete frequencies**  
   The Fourier basis comes from equally spaced rotations around the complex unit circle.

3. **Fourier coefficients as projections**  
   \(X[k]\) measures alignment with a particular Fourier direction.

4. **Squared coefficients as energy**  
   \(|X[k]|^2\) measures squared alignment; Parseval connects the sum of these quantities to the squared norm of the original signal.

5. **Frequency-domain masking**  
   Fourier coordinates can be grouped by period and selectively retained.

6. **Inverse reconstruction**  
   The selected frequency bands transform back into time-domain components that exactly reconstruct the original demeaned signal.

7. **Offline Fourier filtering vs. causal filtering**  
   FFT masking gives sharp frequency separation but uses the whole sample, while SMA and EMA operate causally with smoother frequency responses and lag.

This project studies signal decomposition rather than prediction or trading alpha.

---

# Limitations

The Fourier decomposition is retrospective.

- The full-sample FFT uses future observations relative to historical dates.
- A finite DFT implicitly assumes periodic extension of the sample.
- Sharp frequency masks can create ringing and endpoint effects.
- The 10-day and 60-day boundaries are illustrative.
- Frequency decomposition does not imply that any component is predictable.

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

The core numerical steps remain explicit:

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

Install the dependencies from `requirements.txt`, then execute the notebooks or run

```bash
python scripts/run_notebooks.py
```