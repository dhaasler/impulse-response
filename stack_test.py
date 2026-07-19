import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Line stacking

    This notebook is a test of several stacking methods.

    First select a common velocity axes to resample every spectra to a common velocity axis.
    For now it can be:
    * Velocity axis of the first input line.
    * Custom created by selecting the min and max values of the window, the value for the center channel, and the channel width.

    Then each line gets its own spectra converted to velocity, and resampled via one of the following options:
    * Linear interpolation using `np.interp`
    * Linear interpolation from `specutils.Spectrum`
    * Spline interpolating resample from `specutils.Spectrum`
    * Flux conserving resample from `specutils.Spectrum` (replicates CLASS resampling)
    * Bin reallocation considering channels are finite, physical bins (replicates CLASS resampling). Two options:
        * Using ``specresi``
        * Using custom-made class using only `numpy`

    Finally the spectra are stacked averaging by providing a weighting:
    * Equal weighting
    * Noise-based weighting
    """)
    return


@app.cell
def _():
    import marimo as mo
    from astropy.table import Table
    from astropy.coordinates import SpectralCoord
    import astropy.constants as const
    from specutils import Spectrum
    from specutils.manipulation import LinearInterpolatedResampler
    from specutils.manipulation import FluxConservingResampler
    from specutils.manipulation import SplineInterpolatedResampler
    import astropy.units as u
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import AnchoredText
    from spectres import spectres

    return (
        AnchoredText,
        FluxConservingResampler,
        LinearInterpolatedResampler,
        SpectralCoord,
        Spectrum,
        SplineInterpolatedResampler,
        Table,
        const,
        mo,
        np,
        plt,
        spectres,
        u,
    )


@app.cell
def _(u):
    # User input

    stacking_weighting = 'equal'    # 'equal' or 'sigma'

    stacking_window_params = {
        'min_vel': -20,    # min velocity (km/s) of the window around each line
        'max_vel': 20,    # max velocity (km/s) of the window around each line
    }

    # If False, the program uses the velocity array for the first line and
    # custom_velocity_axes_params are ignored:
    use_custom_velocity_axes = True
    # If use_custom_velocity_axes is True:
    custom_velocity_axes_params = {
        'ref_vel': 0,    # reference velocity to resample velocity axis
        'channel_width': 2    # channel width in velocity (km/s)
    }

    # ---------------------------- Input spectrum data ----------------------------
    spectra_filename = "cross-corr-dats/stack_ch3oh_241_allscans_freq.dat"
    spectra_filename = "cross-corr-dats/POband7-obsfreq.dat"
    x_axis_unit = u.GHz
    # -----------------------------------------------------------------------------

    # ----------------- Define the rest frequencies of the lines ------------------
    #  Make sure you input the units!
    line_rest_freqs = [
    283586.8296,
    283593.1805,
    283777.603,
    283785.4132,
        # 241700.168,
        # 241767.247,
        # 241791.367,
        # 241806.521,
        # 241813.248,
    #    241829.629,
    #    241832.910,
    #    241842.287,
    #    241843.608,
    #    241852.299,
    #    241879.038,
    #    241887.678,
    #    241904.401,
    #    243915.811,
    ]
    line_rest_freqs_unit = u.MHz
    # -----------------------------------------------------------------------------
    return (
        custom_velocity_axes_params,
        line_rest_freqs,
        line_rest_freqs_unit,
        spectra_filename,
        stacking_weighting,
        stacking_window_params,
        use_custom_velocity_axes,
        x_axis_unit,
    )


@app.cell
def _(
    FluxConservingResampler,
    LinearInterpolatedResampler,
    SpectralCoord,
    Spectrum,
    SplineInterpolatedResampler,
    Table,
    class_bin_resample,
    const,
    custom_velocity_axes_params,
    line_rest_freqs,
    line_rest_freqs_unit,
    np,
    spectra_filename,
    spectres,
    stacking_weighting,
    stacking_window_params,
    u,
    use_custom_velocity_axes,
    x_axis_unit,
):
    # Read spectrum data
    spectra_table = Table.read(spectra_filename, format='ascii')
    # spectra_table = Table.read(spectra_filename, format='csv', delimiter="\t")
    spectra_obsfreq = spectra_table.columns[0].data
    spectra_flux = spectra_table.columns[1].data

    freq_array = spectra_obsfreq * x_axis_unit
    flux_array = spectra_flux  

    line_rest_freqs_quant = line_rest_freqs * line_rest_freqs_unit

    v_min = stacking_window_params['min_vel']
    v_max = stacking_window_params['max_vel']

    # Select common velocity axis
    if use_custom_velocity_axes == True:
        # Custom velocity axis with vref in the middle of its channel
        dv = custom_velocity_axes_params['channel_width']
        v_ref = custom_velocity_axes_params["ref_vel"]
        # Calculate steps relative to v_ref to each side
        # Using ceil ensures we fully cover the requested window boundaries
        n_steps_left = int(np.ceil((v_ref - v_min) / dv))
        n_steps_right = int(np.ceil((v_max - v_ref) / dv))
        # Generate step integers relative to the reference channel
        steps = np.arange(-n_steps_left, n_steps_right + 1)
        # Get the common velocity axis anchored at v_ref
        common_velocity = v_ref + (steps * dv)
    else:
        # Get common velocity as the velocity axes of the first line 
        spectra_sc_template = SpectralCoord(spectra_obsfreq, unit=x_axis_unit,
                                            doppler_rest=line_rest_freqs_quant[0],
                                            doppler_convention='radio',)
        common_velocity_value = spectra_sc_template.to(u.km / u.s).value
        slice_mask = ((common_velocity_value >= v_min) &
                      (common_velocity_value <= v_max))
        common_velocity = common_velocity_value[slice_mask]
        # If the axis was in frequency, we need to swap its order so that the velocity
        # array is incremental
        if common_velocity[0] > common_velocity[-1]:
            common_velocity = common_velocity[::-1]

    aligned_slices_linear_np = []
    aligned_slices_linear_specutils = []
    aligned_slices_spline_specutils = []
    aligned_slices_flux_conserving_specutils = []
    aligned_slices_bin_reallocation_spectres = []
    aligned_slices_bin_reallocation_manual = []
    f_slices = []
    v_slices = []

    # Slice spectra around each line and resample them to the common velocity axis
    for f0 in line_rest_freqs_quant:

        # Convert freq arrays into velocity arrays centered on each line
        # 3 ways to do it: 
        #   · Manually with: v = c * (f0 - f) / f0
        #   · Astropy equivalencies.
        #   · SpectralCoord (not optimal: creates a SpectrCoord object for each
        #                    loop that will never be used again)

        # Manually
        # Check if units are both the same physical type (Frequency)
        if x_axis_unit.physical_type != 'frequency' or line_rest_freqs_unit.physical_type != 'frequency':
            raise TypeError("Both variables must be of physical type 'frequency'!")
        current_line_vel_axis_manual = (
            const.c * (f0 - freq_array) / f0).to(u.km / u.s).value

        # SpectralCoord
        spectra_sc_temp = SpectralCoord(spectra_obsfreq, unit=x_axis_unit,
                                        doppler_rest=f0,
                                        doppler_convention='radio',)
        current_line_vel_axis_SC = spectra_sc_temp.to(u.km / u.s).value

        # Astropy equivalency
        current_line_vel_axis_eq = (freq_array).to(u.km / u.s, 
                                    equivalencies=u.doppler_radio(f0)).value


        # Slice portion around the line
        # Since the current method interpolated into a custom-made velocity axis,
        # we do not need to slice, so just renaming for the moment
        v_slice = current_line_vel_axis_SC
        f_slice = flux_array


        # Interpolate the data slice onto the common velocity grid 
        # Ensure the velocity axis is strictly increasing for resampling
        if len(v_slice) > 1:
            if v_slice[0] > v_slice[-1]:
                v_slice = v_slice[::-1]
                f_slice = f_slice[::-1]

            # Baseline each slice before stacking to allow sigma based weighting
            # Define your window boundaries for the baseline
            base_min, base_max = -1.0, 1.0
            # Create a mask specifically matching the baseline region on the common grid
            baseline_mask = (v_slice >= base_min) & (v_slice <= base_max)
            # Calculate the average background level inside this window
            # (Using np.mean here since we want the unweighted baseline value)
            baseline_level = np.mean(f_slice[baseline_mask])
            # Level the spectrum by subtracting the baseline from the whole slice
            f_slice -= baseline_level

            # Linear interpolation using np.interp
            interp_flux_linear_np = np.interp(common_velocity, v_slice, f_slice)

            # Linear interpolation using specutils.Spectrum
            input_spectrum = Spectrum(
                flux=f_slice * u.K, spectral_axis=v_slice * u.km / u.s)
            target_velocity = common_velocity * u.km / u.s
            # Linear resample (nan_fill replicates CLASS edge blanking)
            linear_resampler = LinearInterpolatedResampler(
                extrapolation_treatment='nan_fill')
            resampled_spectrum_linear = linear_resampler(input_spectrum, target_velocity)
            # Extract arrays
            interp_flux_linear_specutils = resampled_spectrum_linear.flux.value

            # Spline interpolating resample  (nan_fill replicates CLASS edge blanking)
            spline_resampler = SplineInterpolatedResampler(
                extrapolation_treatment='nan_fill')
            resampled_spectrum_spline = spline_resampler(input_spectrum, target_velocity)
            # Extract arrays
            interp_flux_spline_specutils = resampled_spectrum_spline.flux.value

            # Flux conserving resample  (nan_fill replicates CLASS edge blanking)
            flux_conserving_resampler = FluxConservingResampler(
                extrapolation_treatment='nan_fill')
            resampled_spectrum_flux_conserving = flux_conserving_resampler(
                input_spectrum, target_velocity)
            # Extract arrays
            interp_flux_flux_conserving_specutils = (
                resampled_spectrum_flux_conserving.flux.value)

            # Using spectres. This replicates the class resampling.
            # CLASS uses a boxcar convolution kernel based on pixel boundaries.
            # specutils and standard numpy.interp assume data points are infinitely
            # sharp \(x, y\) coordinates, whereas GILDAS CLASS views a spectrum as
            # an array of finite, physical channel bins. To exactly match CLASS
            # resampling in Python, you must shift from coordinate-based
            # interpolation to bin-reallocation and fractional overlapping area
            # calculations.
            interp_flux_bin_reallocation_spectres = spectres(
                common_velocity, v_slice, f_slice, fill=np.nan)
            # I can also use a manual class that does this exact same thing
            interp_flux_bin_reallocation_manual = class_bin_resample(
                v_slice, f_slice, common_velocity)

            aligned_slices_linear_np.append(
                interp_flux_linear_np)
            aligned_slices_linear_specutils.append(
                interp_flux_linear_specutils)
            aligned_slices_spline_specutils.append(
                interp_flux_spline_specutils)
            aligned_slices_flux_conserving_specutils.append(
                interp_flux_flux_conserving_specutils)
            aligned_slices_bin_reallocation_spectres.append(
                interp_flux_bin_reallocation_spectres)
            aligned_slices_bin_reallocation_manual.append(
                interp_flux_bin_reallocation_manual)
            f_slices.append(f_slice)
            v_slices.append(v_slice)

        else:
            print(f"Warning: Line at {f0} is outside the range of your spectrum.")

    every_aligned_slices = [
        aligned_slices_linear_np,
        aligned_slices_linear_specutils,
        aligned_slices_spline_specutils,
        aligned_slices_flux_conserving_specutils,
        aligned_slices_bin_reallocation_spectres,
        aligned_slices_bin_reallocation_manual,
    ]

    # Stack the aligned slices
    stacked_spectra = []
    for aligned_slices in every_aligned_slices:
        if stacking_weighting == 'equal':
            weights = None
        elif stacking_weighting == 'sigma':
            std_devs = [np.std(slice) for slice in aligned_slices] # estimate noise from slice
            weights = 1.0 / np.array(std_devs)**2
        else: weights = None
        stacked_spectrum = np.average(aligned_slices, axis=0, weights=weights)
        stacked_spectra.append(stacked_spectrum)

    stacked_spectra_names = [
        "linear_np",
        "linear_specutils",
        "spline_specutils",
        "flux_conserving_specutils",
        "bin_reallocation_spectres",
        "bin_reallocation_manual",
    ]
    return common_velocity, stacked_spectra, stacked_spectra_names, v_ref


@app.cell
def _(
    AnchoredText,
    common_velocity,
    plt,
    stacked_spectra,
    stacked_spectra_names,
    use_custom_velocity_axes,
    v_ref,
):
    # 5. Plot the Stacked Result
    main_fig, main_fig_axes = plt.subplots(6, 1, figsize=(10,40))

    for ax, spec, name in zip(main_fig_axes, stacked_spectra, stacked_spectra_names):
        ax.plot(common_velocity, spec, drawstyle='steps-mid',
                        color='black', lw=2)
        if use_custom_velocity_axes:
            ax.axvline(v_ref, color='red', linestyle='--', alpha=0.7)
        ax.grid(True, alpha=0.3)
        # Label box
        anchored_text = AnchoredText(
            f'{name}', 
            loc='upper left',          # Snaps it perfectly inside the top-left corner
            frameon=True,              # Ensures the background box is visible
            pad=0.5,                   # Padding inside the box around the text
            borderpad=0.4,             # Padding between the box and the axes edge
            prop=dict(
                size=11,
            ),
        )
        anchored_text.patch.set_boxstyle("round,pad=0")
        anchored_text.patch.set_facecolor("white")
        anchored_text.patch.set_edgecolor("lightgray")
        anchored_text.patch.set_linewidth(1)
        ax.add_artist(anchored_text)

    main_fig_axes[5].set_xlabel('Velocity (km/s)')
    main_fig_axes[5].set_ylabel('Flux / Intensity')
    main_fig_axes[0].set_title('Stacked Molecular Emission Lines')
    # main_fig_ax.set_xlim(-20, 20)
    #plt.ylim(-0.015, 0.020)
    plt.show()
    return


@app.cell
def _(np):
    def class_bin_resample(orig_centers, orig_flux, target_centers):
        """
        Resamples spectra by calculating exact geometric overlapping channel
        fractions, created to match the default physical bin allocation of CLASS.
        """
        # Calculate channel widths (assuming uniform grids)
        orig_width = np.abs(orig_centers[1] - orig_centers[0])
        target_width = np.abs(target_centers[1] - target_centers[0])

        # Find boundary edges of every channel bin
        orig_edges = np.concatenate([
            orig_centers - orig_width/2,
            [orig_centers[-1] + orig_width/2]
        ])
        target_edges = np.concatenate([
            target_centers - target_width/2,
            [target_centers[-1] + target_width/2]
        ])

        resampled_flux = np.zeros(len(target_centers))

        # Calculate fractional intersections channel by channel
        for i in range(len(target_centers)):
            t_low, t_high = target_edges[i], target_edges[i+1]

            # Flag as NaN if out of bounds bounds
            if t_high <= orig_edges[0] or t_low >= orig_edges[-1]:
                resampled_flux[i] = np.nan
                continue

            total_overlap = 0.0
            weighted_sum = 0.0

            for j in range(len(orig_centers)):
                o_low, o_high = orig_edges[j], orig_edges[j+1]

                # Find overlapping segment between target bin i and original bin j
                overlap = min(t_high, o_high) - max(t_low, o_low)

                if overlap > 0:
                    total_overlap += overlap
                    weighted_sum += overlap * orig_flux[j]

            if total_overlap > 0:
                resampled_flux[i] = weighted_sum / total_overlap
            else:
                resampled_flux[i] = np.nan

        return resampled_flux

    return (class_bin_resample,)


if __name__ == "__main__":
    app.run()
