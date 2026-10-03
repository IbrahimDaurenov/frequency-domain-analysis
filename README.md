# Frequency-Domain Analysis of Stock Returns

This project treats daily SPY log returns as a discrete-time signal and studies them in the Fourier basis.

The main idea is simple:

**returns → FFT → frequency bands → inverse FFT → reconstructed time-scale components**

Instead of using the FFT only to plot a spectrum, I use it to split the observed return signal into low-, medium-, and high-frequency components and then reconstruct each component back in the time domain.

I also compare the low-frequency Fourier reconstruction with causal SMA and EMA filters.

---

## 1. From returns to Fourier coordinates

For adjusted closing price \(P_t\), daily log return is

$$
r_t = \log P_t - \log P_{t-1}.
$$

Before applying the FFT, I remove the sample mean:

$$
x_t = r_t - \bar r.
$$

The FFT changes coordinates from the time domain to the Fourier basis:

$$
x_t
\quad \longrightarrow \quad
X_k.
$$

For a sample of length \(N\), Fourier bin \(k\) corresponds approximately to

$$
f_k = \frac{k}{N}
$$

cycles per trading day, or equivalently to period

$$
T_k = \frac{N}{k}
$$

trading days.

This makes the Fourier coefficients easy to interpret by time scale.

---

## 2. Frequency bands

I separate the Fourier coefficients into three period ranges:

| Component | Period |
|---|---:|
| Low frequency | \(T > 60\) trading days |
| Mid frequency | \(10 < T \le 60\) trading days |
| High frequency | \(2 \le T \le 10\) trading days |

For example, the low-frequency spectrum is

$$
X_k^{low} =
\begin{cases}
X_k, & T_k > 60, \\
0, & \text{otherwise}.
\end{cases}
$$

The same masking procedure gives \(X^{mid}\) and \(X^{high}\).

Applying the inverse FFT gives the corresponding time-domain signals:

$$
x^{low}_t = \text{IFFT}(X^{low}),
$$

$$
x^{mid}_t = \text{IFFT}(X^{mid}),
$$

$$
x^{high}_t = \text{IFFT}(X^{high}).
$$

Because the masks partition the Fourier coefficients,

$$
x_t
\approx
x_t^{low}
+
x_t^{mid}
+
x_t^{high}.
$$

In the actual calculation, the maximum reconstruction error is approximately

$$
4.2 \times 10^{-17},
$$

so the original demeaned return signal is recovered to floating-point precision.

---

## 3. What the Fourier representation looks like

The squared magnitude

$$
|X_k|^2
$$

measures how strongly the return signal is represented by the Fourier direction associated with bin \(k\).

Equivalently, it is the squared magnitude of the signal's projection onto that Fourier component.

The plot below shows this quantity against period rather than bin number, making the different time scales easier to interpret.

![Fourier power by period](figures/01_power_spectrum.png)

The purpose of this figure is not to claim that SPY has a deterministic cycle at a particular period. It shows how the observed finite return series is distributed across Fourier time scales.

---

## 4. Reconstructing the return signal by time scale

The inverse FFT makes the frequency decomposition visible in the original time domain.

![Low, mid and high frequency return components](figures/02_return_components.png)

The difference between the components is clear:

- **Low frequency:** slowly varying movements over horizons longer than roughly 60 trading days.
- **Mid frequency:** oscillations on roughly 10–60 day horizons.
- **High frequency:** short-horizon fluctuations on roughly 2–10 day horizons.

The original daily return series is the combination of these components.

This is the central result of the project: the low-, mid-, and high-frequency curves are not unrelated smoothers. They are reconstructed from different parts of the **same Fourier representation** of the original signal.

---

## 5. Cumulative contribution of each component

Daily returns are noisy, so the decomposition becomes easier to interpret after cumulative summation.

![Cumulative Fourier reconstruction](figures/03_cumulative_reconstruction.png)

The low-frequency component follows much of the broad shape of the cumulative demeaned return path.

The intuition is straightforward: high-frequency components change sign frequently, so much of their effect cancels when summed over long intervals. Low-frequency components persist for longer periods and therefore contribute more strongly to the large-scale shape.

The lower panel progressively reconstructs the signal:

$$
low
\quad \rightarrow \quad
low + mid
\quad \rightarrow \quad
low + mid + high.
$$

The final combination recovers the original demeaned cumulative return series.

These curves are cumulative **demeaned log returns**, not the SPY price itself.

---

## 6. Fourier filtering vs. SMA and EMA

The Fourier decomposition above uses a sharp low-frequency cutoff:

$$
T > 60 \text{ trading days}.
$$

Its cutoff angular frequency is

$$
\omega_c = \frac{2\pi}{60}.
$$

To make the comparison with time-domain filters more meaningful, I choose SMA and EMA parameters whose gain is approximately

$$
\frac{1}{\sqrt{2}}
$$

at the same cutoff frequency.

This gives approximately:

$$
M_{SMA} = 27,
$$

and

$$
\alpha_{EMA} \approx 0.0993.
$$

The EMA parameter corresponds to an effective span of about 19.1 observations.

![Fourier low-pass versus matched SMA and EMA](figures/04_filter_comparison.png)

The filters behave differently even though their cutoff frequencies are approximately matched.

### Fourier low-pass

The Fourier reconstruction uses a hard frequency mask:

- keep periods above 60 days,
- remove the rest.

This gives sharp frequency separation, but the calculation uses the full sample. It is therefore an **offline decomposition**, not a real-time trading indicator.

### SMA

The SMA is a finite impulse response filter:

$$
s_t =
\frac{1}{M}
\sum_{j=0}^{M-1} r_{t-j}.
$$

Its frequency response has zeros and side lobes.

### EMA

The EMA is an infinite impulse response filter:

$$
s_t =
\alpha r_t
+
(1-\alpha)s_{t-1}.
$$

Expanding the recursion gives impulse-response weights

$$
h_n = \alpha(1-\alpha)^n.
$$

The weights decay exponentially, producing a smooth low-pass frequency response.

Unlike the full-sample Fourier decomposition, both SMA and EMA are causal: their value at time \(t\) uses only current and past observations.

---

## 7. Main takeaways

This project demonstrates four basic Signals & Systems ideas on a financial time series:

1. **FFT as a change of basis.**  
   Daily returns can be represented by Fourier coefficients instead of time-domain samples.

2. **Frequency-domain masking.**  
   Fourier coefficients can be separated according to their associated periods.

3. **Inverse reconstruction.**  
   Low-, mid-, and high-frequency components can be transformed back into the time domain and sum to the original demeaned signal.

4. **Frequency-domain vs. causal filtering.**  
   A sharp Fourier cutoff, SMA, and EMA all isolate slower variation, but they have different frequency responses and different causality properties.

The project is a signal-decomposition study, not a forecasting model or trading strategy.

---

## Limitations

The full-sample FFT decomposition is retrospective.

- It uses the complete sample rather than only information available at each historical date.
- A finite FFT treats the sample as periodically extended, so endpoints can create wraparound effects.
- Sharp frequency masks can produce ringing.
- The 10-day and 60-day boundaries are illustrative choices rather than economically estimated parameters.
- Separating a return series by frequency does not by itself imply predictability or trading alpha.

---

## Repository

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

The notebooks keep the main mathematical objects visible in code:

```python
x = returns - returns.mean()

X = np.fft.rfft(x)
power = np.abs(X) ** 2

X_low = np.where(low_mask, X, 0)
x_low = np.fft.irfft(X_low, n=len(x))
```

NumPy uses the opposite sign convention from the Fourier matrix convention used in my linear algebra notes; using `rfft` and `irfft` consistently gives the same real-valued reconstruction.

---

## Run

Install the dependencies in `requirements.txt`, then run the notebooks or execute:

```bash
python scripts/run_notebooks.py
```