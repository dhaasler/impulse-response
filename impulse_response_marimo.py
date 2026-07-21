import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Impulse response
    """)
    return


@app.cell
def _(mo):
    # File pickers

    file_picker_SLIM = mo.ui.file(filetypes=[".csv"], kind="area")
    file_picker_spectra = mo.ui.file(multiple=True, kind="area")

    mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("### 📂 Select SLIM File"),
                    mo.md("_Drop your SLIM file directly below, or click to browse_"),
                    file_picker_SLIM,
                ]
            ),
            mo.vstack(
                [
                    mo.md("### 📂 Select Spectra File(s)"),
                    mo.md("_Drop your spectrum file(s) directly below, or click to browse_"),
                    file_picker_spectra,
                ]
            ),
        ],
        widths="equal", # Makes both columns share equal width
        align="start",  # Keeps titles aligned at the top
    )
    return file_picker_SLIM, file_picker_spectra


@app.cell
def _(freqs, mo, stacking_freqs):
    # Show Stack freqs list if list is set to None

    if stacking_freqs is None:
        freq_selector = mo.ui.multiselect(
            options=freqs,
            value=freqs,
            label="Frequencies",
        )

        stacking_output = mo.vstack(
            [
                mo.md(
                    """
                    ### Select Stacking Frequencies
                    Choose which frequencies you want to include in the stack analysis below:
                    """
                ),
                freq_selector,
            ]
        )
    else:
        stacking_output = None

    stacking_output
    return (freq_selector,)


@app.cell
def _(freq_selector, stacking_freqs):
    # Show Stack freqs list if list is set to None
    if stacking_freqs is None:
        selected_stacking_freqs = freq_selector.value
    else:
        selected_stacking_freqs = stacking_freqs
    return (selected_stacking_freqs,)


@app.cell
def _(u):
    # User input (marimo notebook version)

    # Set SLIM data
    molecule = 'PO,v=0'  # Formula string from MADCUBA
    slim_freq_unit = u.MHz

    spectra_freq_unit = u.GHz
    spectra_flux_unit = u.Jy

    # Stacking freq list
    # Here the user can select which transitions to use for the stacking.
    # If set to 'all', the program uses every transition found within the spectra
    # files
    # If set to None, or empty, the program outputs a list of found frequencies to select
    # stacking_freqs = [
    #     # 109252.22,
    #     152656.979,
    #     152680.282,
    #     152855.454,
    #     152888.128,
    #     283586.8296,
    #     283593.1805,
    #     283777.603,
    #     283785.4132,
    # ]
    stacking_freqs = None
    stacking_freqs_unit = u.MHz


    # Stacking parameters

    stacking_weighting = 'equal'    # 'equal' or 'sigma'

    stacking_window_params = {
        'min_vel': -60,    # min velocity (km/s) of the window around each line
        'max_vel': 60,    # max velocity (km/s) of the window around each line
    }

    baseline_window_params = {
        'min_vel': -1,    # min velocity (km/s) of the window around each line
        'max_vel': 1,    # max velocity (km/s) of the window around each line
    }

    # Resampling parameters

    # If False, the program uses the velocity array for the first line and
    # custom_velocity_axes_params are ignored:
    use_custom_velocity_axes = False
    # If use_custom_velocity_axes is True:
    custom_velocity_axes_params = {
        'ref_vel': 0,    # reference velocity to resample velocity axis
        'channel_width': 1    # channel width in velocity (km/s)
    }

    resample_method = 'linear'  # 'linear' (default) or 'flux-conserving' (CLASS)

    # Logging
    view_each_transition = True
    return (
        custom_velocity_axes_params,
        molecule,
        resample_method,
        slim_freq_unit,
        spectra_flux_unit,
        spectra_freq_unit,
        stacking_freqs,
        stacking_freqs_unit,
        stacking_weighting,
        stacking_window_params,
        use_custom_velocity_axes,
        view_each_transition,
    )


@app.cell(hide_code=True)
def _():
    # # User input (script version)

    # # Set SLIM data
    # molecule = 'PO,v=0'  # Formula string from MADCUBA
    # slim_freq_unit = u.MHz
    # # slim_filename = 'cross-corr-dats/slim_table_region_10.csv'
    # # slim_filename = 'cross-corr-dats/SLIM-table-SO.csv'

    # # Set spectra data (can be multiple files)
    # # spectra_filenames = [
    # #     'cross-corr-dats/01_IRAS_16293-2422_spw27.dat',
    # #     'cross-corr-dats/01_IRAS_16293-2422_spw29.dat',
    # #     # 'cross-corr-dats/POband7-obsfreq.dat',
    # # ]
    # spectra_freq_unit = u.GHz
    # spectra_flux_unit = u.Jy

    # # Stacking freq list
    # # Here the user can select which transitions to use for the stacking.
    # # If set to 'all', the program uses every transition found within the spectra
    # # files
    # # If set to None, or empty, the program outputs a list of found frequencies to select
    # stacking_freqs = [
    #     # 109252.22,
    #     152656.979,
    #     152680.282,
    #     152855.454,
    #     152888.128,
    #     283586.8296,
    #     283593.1805,
    #     283777.603,
    #     283785.4132,
    # ]
    # stacking_freqs_unit = u.MHz


    # # Stacking parameters

    # stacking_weighting = 'equal'    # 'equal' or 'sigma'

    # stacking_window_params = {
    #     'min_vel': -60,    # min velocity (km/s) of the window around each line
    #     'max_vel': 60,    # max velocity (km/s) of the window around each line
    # }

    # baseline_window_params = {
    #     'min_vel': -1,    # min velocity (km/s) of the window around each line
    #     'max_vel': 1,    # max velocity (km/s) of the window around each line
    # }

    # # Resampling parameters

    # # If False, the program uses the velocity array for the first line and
    # # custom_velocity_axes_params are ignored:
    # use_custom_velocity_axes = False
    # # If use_custom_velocity_axes is True:
    # custom_velocity_axes_params = {
    #     'ref_vel': 0,    # reference velocity to resample velocity axis
    #     'channel_width': 1    # channel width in velocity (km/s)
    # }

    # resample_method = 'linear'  # 'linear' (default) or 'flux-conserving' (CLASS)

    # # Logging
    # view_each_transition = True
    return


@app.cell
def _(BytesIO, Table, file_picker_SLIM, mo):
    # The SLIM Gate: Stop immediately if the tuple is empty

    mo.stop(
        len(file_picker_SLIM.value) == 0, 
        mo.md("### Please upload a SLIM file above to begin...")
    )

    # 2. The Processing: This code will NEVER run unless a file is uploaded
    try:
        # 1. Grab the raw byte contents of the first uploaded file
        slim_raw_bytes = file_picker_SLIM.contents(0)

        # 2. Wrap the bytes into an in-memory virtual file stream
        slim_file = BytesIO(slim_raw_bytes)

        # 3. Read the table
        slim_table = Table.read(slim_file, format='csv', delimiter=",")

    except Exception as e:
        # If the file is corrupted or not a valid FITS, catch the error and show it
        mo.stop(True, mo.md(f"❌ **Error parsing SLIM file:** {str(e)}"))

    mo.stop(
        len(file_picker_SLIM.value) == 0, 
        mo.md("### Please upload at lest one spectrum file above to begin...")
    )
    return (slim_table,)


@app.cell
def _(
    BytesIO,
    Spectrum,
    Table,
    file_picker_spectra,
    mo,
    spectra_flux_unit,
    spectra_freq_unit,
):
    # The SLIM Gate: Stop immediately if the tuple is empty

    mo.stop(
        len(file_picker_spectra.value) == 0, 
        mo.md("### Please upload one or more spectra files above to begin...")
    )

    # 2. The Processing: This code will NEVER run unless a file is uploaded
    try:
        # 1. Grab raw bytes for ALL uploaded files using their index/length
        # or iterate directly over file_picker_SLIM.value
        spectra_filenames = [
            BytesIO(file_picker_spectra.contents(i)) 
            for i in range(len(file_picker_spectra.value))
        ]
    
        # 3. Read the tables
        # Store Spectrum and Table just in case.
        spectra_tables = []
        spectra = []
        for filename in spectra_filenames:
            spectrum_table = Table.read(filename, format="ascii")
            spectra_tables.append(spectrum_table)
            spectra.append(
                Spectrum(
                    spectral_axis=spectrum_table.columns[0].data * spectra_freq_unit,
                    flux=spectrum_table.columns[1].data * spectra_flux_unit,
                )
            )

    except Exception as e:
        # If the file is corrupted or not a valid FITS, catch the error and show it
        mo.stop(True, mo.md(f"❌ **Error parsing spectrum file:** {str(e)}"))
    return (spectra,)


@app.cell(hide_code=True)
def _(lines_fig, main_fig, mo, peak_shift, v_center):
    # Show results
    main_view = mo.vstack(
        [
            mo.md("## Impulse Response results"),
            mo.hstack(
                [
                    # mo.stat(
                    #     label="Peak S/N", value=f"{peak_sn:.3f} km/s"
                    # ),
                    mo.stat(
                        label="Recovered Shift", value=f"{peak_shift:.3f} km/s"
                    ),
                    mo.stat(
                        label="Line Centroid", value=f"{v_center:.3f} km/s"
                    ),
                    # mo.stat(
                    #     label="LDetected velocity of first comp", value=f"{peak_vel:.3f:.3f} km/s"
                    # ),
                ],
                justify="start",
            ),
            main_fig,
        ]
    )

    # Optional figure showing selected lines

    # Render accordion only if lines_fig exists
    if "lines_fig" in locals() and lines_fig is not None:
        optional_view = mo.accordion(
            {
                "🔍 View Individual Spectra Breakdown": mo.vstack(
                    [
                        mo.md("Detailed plot showing each spectrum used in the impulse response calculation:"),
                        lines_fig,
                    ]
                )
            }
        )
        output = mo.vstack([main_view, optional_view])
    else:
        output = main_view

    output
    return


@app.cell
def _():
    # frequency_selector
    return


@app.cell
def _():
    # selected_freqs = frequency_selector.value

    # mask = np.isin(tbl["Frequency"], selected_freqs)

    # filtered_table = tbl[mask]

    # filtered_table
    return


@app.cell
def _():
    # # Example table
    # tbl = Table({
    #     "Frequency": [100, 200, 300, 400],
    #     "Flux": [1.2, 1.3, 2.1, 0.9],
    # })

    # # Get unique frequencies
    # freqs = sorted(np.unique(tbl["Frequency"]))

    # # Create widget
    # frequency_selector = mo.ui.multiselect(
    #     options=freqs,
    #     value=freqs,          # preselect all (optional)
    #     label="Select frequencies"
    # )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Hidden (seriously, don't look)
    """)
    return


@app.cell
def _():
    # imports

    import marimo as mo

    from astropy.table import Table
    from astropy.coordinates import SpectralCoord
    import astropy.units as u
    from dataclasses import dataclass, field
    from io import BytesIO
    import matplotlib.pyplot as plt
    import numpy as np
    from specutils import Spectrum
    from specutils.manipulation import LinearInterpolatedResampler
    from specutils.manipulation import FluxConservingResampler
    from typing import Optional

    return (
        BytesIO,
        FluxConservingResampler,
        LinearInterpolatedResampler,
        Optional,
        SpectralCoord,
        Spectrum,
        Table,
        dataclass,
        field,
        mo,
        np,
        plt,
        u,
    )


@app.cell
def _(Optional, Spectrum, dataclass, field, np, u):
    # Aux classes and functions

    @dataclass
    class LineSpectrum:
        observed: Spectrum
        model: Spectrum

        # Define your measurement fields here (defaulting to None)
        noise: Optional[u.Quantity] = None
        snr: Optional[float] = None
        line_center: Optional[u.Quantity] = None

        # This safely initializes an empty dictionary for every new instance
        meta: dict = field(default_factory=dict)

        def to_vel(self):
            velocity_line = LineSpectrum(
                observed=Spectrum(
                    spectral_axis=self.observed.velocity.copy(),
                    flux=self.observed.flux.copy(),
                    rest_value=self.observed.rest_value,
                    velocity_convention=self.observed.velocity_convention,
                ),
                model=Spectrum(
                    spectral_axis=self.model.velocity.copy(),
                    flux=self.model.flux.copy(),
                    rest_value=self.model.rest_value,
                    velocity_convention=self.observed.velocity_convention,
                ),
                meta=self.meta.copy(),
            )
            return velocity_line

        def reverse(self):
            reversed_line = LineSpectrum(
                observed=Spectrum(
                    spectral_axis=self.observed.spectral_axis[::-1].copy(),
                    flux=self.observed.flux[::-1].copy(),
                    rest_value=self.observed.rest_value,
                    velocity_convention=self.observed.velocity_convention,
                ),
                model=Spectrum(
                    spectral_axis=self.model.spectral_axis[::-1].copy(),
                    flux=self.model.flux[::-1].copy(),
                    rest_value=self.model.rest_value,
                    velocity_convention=self.observed.velocity_convention,
                ),
                meta=self.meta.copy(),
            )
            return reversed_line

        def resample(self, resampler, new_axis):

            # Change units of spectra to new_axis units

            resampled_observed = resampler(self.observed, new_axis)
            resampled_model = resampler(self.model, new_axis)

            # First velocity convention has to be set, then the rest_value setter.
            if hasattr(self.observed, 'velocity_convention'):
                resampled_observed = resampled_observed.with_velocity_convention(
                    self.observed.velocity_convention)
                resampled_model = resampled_model.with_velocity_convention(
                    self.model.velocity_convention)
            if hasattr(self.observed, 'rest_value'):
                resampled_observed.rest_value = self.observed.rest_value
                resampled_model.rest_value = self.model.rest_value

            return LineSpectrum(
                observed=resampled_observed,
                model=resampled_model,
                meta=self.meta.copy(),
            )

        @property
        def spectral_axis(self):
            return self.observed.spectral_axis

        @property
        def flux(self):
            return self.observed.flux

        @property
        def rest_value(self):
            return self.observed.rest_value

    def gaussian_profile(vel_array, intensity, velocity, width):
        sigma = width / (2 * np.sqrt(2 * np.log(2)))
        return intensity * np.exp(-(vel_array - velocity)**2 / (2 * sigma**2))

    return LineSpectrum, gaussian_profile


@app.cell
def _(
    molecule,
    np,
    slim_freq_unit,
    slim_table,
    spectra,
    spectra_freq_unit,
    stacking_freqs_unit,
):
    # Data preparation

    # Check that all freq units are both the same physical type (Frequency)
    if (spectra_freq_unit.physical_type != 'frequency'
        or stacking_freqs_unit.physical_type != 'frequency'
        or slim_freq_unit.physical_type != 'frequency'):
        raise TypeError(
            "To avoid over-complicating the user input parameters, freq variables " +
            "must be of physical type 'frequency'. Use spectra files with X axis " +
            "in observed frequency."
        )

    # SLIM and Spectra preparation

    # slim_table = Table.read(slim_filename, format='csv', delimiter=",")  # moved to cell on top for notebook
    slim_table["Frequency"].unit = slim_freq_unit

    # Molecule filter
    molecule_filter = (slim_table["Formula"] == molecule)

    # Frequency filter
    # # Store Spectrum and Table just in case.  # moved to cell on top for notebook
    # spectra_tables = []
    # spectra = []
    # for filename in spectra_filenames:
    #     spectrum_table = Table.read(filename, format="ascii")
    #     spectra_tables.append(spectrum_table)
    #     spectra.append(
    #         Spectrum(
    #             spectral_axis=spectrum_table.columns[0].data * spectra_freq_unit,
    #             flux=spectrum_table.columns[1].data * spectra_flux_unit,
    #         )
    #     )
    freq_range_filter = np.zeros(len(slim_table), dtype=bool)
    for _spectrum in spectra:
        spec_freq = _spectrum.spectral_axis
        freq_range_filter |= (
            (slim_table["Frequency"] > spec_freq.min()) &
            (slim_table["Frequency"] < spec_freq.max())
        )
    slim_table_mol_freq = slim_table[molecule_filter & freq_range_filter]
    freqs = sorted(np.unique(slim_table_mol_freq["Frequency"]))
    return freqs, slim_table_mol_freq


@app.cell
def _(
    np,
    selected_stacking_freqs,
    slim_table_mol_freq,
    stacking_freqs_unit,
    u,
):
    # Selected transitions filter
    selected_freqs = selected_stacking_freqs * stacking_freqs_unit
    table_freqs = slim_table_mol_freq["Frequency"].to(u.GHz).value
    selected_freqs_filter = np.zeros(len(table_freqs), dtype=bool)
    for f in selected_freqs.to(u.GHz).value:
        selected_freqs_filter |= np.isclose(
            table_freqs,
            f,
            rtol=0,
            atol=1e-6,  # Hz-precision when comparing MHz
        )
    slim_table_stacking = slim_table_mol_freq[selected_freqs_filter]
    return (slim_table_stacking,)


@app.cell
def _(
    LineSpectrum,
    SpectralCoord,
    Spectrum,
    gaussian_profile,
    np,
    slim_table_stacking,
    spectra,
    spectra_flux_unit,
    u,
):
    # Data preparation 2

    group_col = "Transition" if "Transition" in slim_table_stacking.colnames else "Frequency"
    slim_table_stacking_grouped = slim_table_stacking.group_by(group_col)

    lines = []
    for key, group in zip(slim_table_stacking_grouped.groups.keys,
                          slim_table_stacking_grouped.groups):
        # Here group is each transition table of the molecule

        # Rest frequency of this transition
        rest_freq = group["Frequency"].quantity[0]

        # Check if all rows are the same transition
        group_freqs = group["Frequency"].quantity
        if "Transition" in group.colnames:
            if not np.all(group["Transition"] == group["Transition"][0]):
                raise ValueError(
                    f"Transitions check failed: they differ between velocity components"
                )
        elif not np.allclose(
            group_freqs.to_value(u.MHz), group_freqs[1].to_value(u.MHz),
            rtol=1e-12, atol=1e-12):  # This has precision up to the Hz on MHz arrays
                raise ValueError(
                    f"Transitions check failed: they differ between velocity components"
                )

        component_lines = np.column_stack([
            group["Intensity"],
            group["Velocity"],
            group["Width"],
        ])

        for _spectrum in spectra:

            # Check if transition is inside this spectrum
            if not (
                _spectrum.spectral_axis.min() <= rest_freq <= _spectrum.spectral_axis.max()
            ):
                continue

            found = True

            # Create models

            # Velocity axis for this spectrum
            spec_vel_value = _spectrum.spectral_axis.to(
                u.km / u.s,
                doppler_rest=rest_freq,
                doppler_convention="radio",
            ).value
            # Observed flux
            _spectrum_flux_value = _spectrum.flux.value
            # Create Gaussian model
            model = np.zeros_like(spec_vel_value)

            for intensity, vel, width in component_lines:
                model += gaussian_profile(spec_vel_value, intensity, vel, width)

            # Create the LineSpectrum objects
            observed_spectrum = Spectrum(
                spectral_axis=SpectralCoord(
                    _spectrum.spectral_axis,
                    doppler_rest=rest_freq,
                    doppler_convention="radio",
                ),
                flux=_spectrum.flux,
                rest_value=rest_freq,
                velocity_convention="radio",
            )
            model_spectrum = Spectrum(
                spectral_axis=SpectralCoord(
                    _spectrum.spectral_axis,
                    doppler_rest=rest_freq,
                    doppler_convention="radio",
                ),
                flux=model * spectra_flux_unit,
                rest_value=rest_freq,
                velocity_convention="radio",
            )
            line = LineSpectrum(
                observed=observed_spectrum,
                model=model_spectrum,
            )
            lines.append(line)

        if not found:
            raise RuntimeError(
                f"Transition at {rest_freq} was not found in any selected spectrum."
            )
    return lines, model


@app.cell
def _(
    custom_velocity_axes_params,
    lines,
    np,
    stacking_window_params,
    u,
    use_custom_velocity_axes,
):
    # Prepare common velocity axis

    v_min = stacking_window_params['min_vel']
    v_max = stacking_window_params['max_vel']

    # Prepare slices common velocity axes
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
        # spectra_sc_template = SpectralCoord(spectra_obsfreq, unit=x_axis_unit,
        #                                     doppler_rest=line_rest_freqs_quant[0],
        #                                     doppler_convention='radio',)
        common_velocity_value = lines[0].spectral_axis.to(u.km / u.s).value
        # common_velocity_value = spectra_sc_template.to(u.km / u.s).value
        slice_mask = ((common_velocity_value >= v_min) &
                      (common_velocity_value <= v_max))
        common_velocity = common_velocity_value[slice_mask]
        # If the axis was in frequency, we need to swap its order so that the velocity
        # array is incremental
        if common_velocity[0] > common_velocity[-1]:
            common_velocity = common_velocity[::-1]

    resample_velocity = common_velocity * u.km / u.s
    return resample_velocity, v_ref


@app.cell
def _(
    FluxConservingResampler,
    LinearInterpolatedResampler,
    lines,
    resample_method,
    resample_velocity,
    u,
):
    # Resample every line to the same velocity axis

    linear_resampler = LinearInterpolatedResampler(
        extrapolation_treatment='nan_fill')
    flux_conserving_resampler = FluxConservingResampler(
        extrapolation_treatment='nan_fill')

    lines_resampled = []
    # Slice spectra around each line and resample them to the common velocity axis
    for _line in lines:

        _v_slice = _line.spectral_axis.to(u.km / u.s).value.copy()

        # Interpolate the data onto the common velocity grid slice
        # Ensure the velocity axis is strictly increasing for resampling
        # Ensure increasing velocity axis
        if (len(_v_slice) > 1 and _v_slice[0] > _v_slice[-1]):
            current_line = _line.reverse()
        else:
            current_line = _line

        # Resample line
        if resample_method == 'linear':
            line_resampled = current_line.to_vel().resample(
                linear_resampler, resample_velocity)
        elif resample_method == 'flux-conserving':
            line_resampled = current_line.to_vel().resample(
                flux_conserving_resampler, resample_velocity)

        # Store resampled lines
        lines_resampled.append(line_resampled)
    return (lines_resampled,)


@app.cell
def _(LineSpectrum, Spectrum, lines_resampled, np, stacking_window_params, u):
    # Apply a baseline each line

    lines_resampled_baselined = []
    for _line in lines_resampled:

        _f_slice = _line.observed.flux.value.copy()
        _v_slice = _line.observed.spectral_axis.to(u.km / u.s).value.copy()

        # Baseline each slice before stacking to allow sigma based weighting
        # Define your window boundaries for the baseline
        base_min = stacking_window_params['min_vel']
        base_max = stacking_window_params['max_vel']
        # Create a mask specifically matching the baseline region on the common grid
        baseline_mask = (_v_slice >= base_min) & (_v_slice <= base_max)
        # Calculate the average background level inside this window
        # (Using np.mean here since we want the unweighted baseline value)
        baseline_level = np.mean(_f_slice[baseline_mask])
        # Level the spectrum by subtracting the baseline from the whole slice
        _f_slice -= baseline_level

        line_resampled_baselined = LineSpectrum(
            observed=Spectrum(
                spectral_axis=_line.spectral_axis.copy(),
                flux=_f_slice * _line.flux.unit,
                rest_value=_line.rest_value.copy(),
                velocity_convention=_line.observed.velocity_convention,
            ),
            model=Spectrum(
                spectral_axis=_line.spectral_axis.copy(),
                flux=_line.model.flux.copy(),
                rest_value=_line.rest_value.copy(),
                velocity_convention=_line.model.velocity_convention,
            ),
            meta=_line.meta.copy(),
        )
        lines_resampled_baselined.append(line_resampled_baselined)
    return (lines_resampled_baselined,)


@app.cell
def _(
    LineSpectrum,
    Spectrum,
    lines_resampled_baselined,
    np,
    spectra_flux_unit,
    stacking_weighting,
):
    # Stack the spectra and model

    obs_slices = [_line.observed.flux.to(spectra_flux_unit).value.copy() for _line in lines_resampled_baselined]
    model_slices = [_line.model.flux.to(spectra_flux_unit).value.copy() for _line in lines_resampled_baselined]

    if stacking_weighting == 'equal':
        weights = None
    elif stacking_weighting == 'sigma':
        std_devs = [np.std(slice) for slice in obs_slices]  # estimate noise from slice
        weights = 1.0 / np.array(std_devs)**2
    else: weights = None

    stacked_observed = np.average(obs_slices, axis=0, weights=weights)
    stacked_model = np.average(model_slices, axis=0, weights=weights)

    template_line = lines_resampled_baselined[0]
    line_stacked = LineSpectrum(
        observed=Spectrum(
            spectral_axis=template_line.spectral_axis.copy(),
            flux=stacked_observed * template_line.observed.unit,
            rest_value=template_line.rest_value.copy(),
            velocity_convention=template_line.observed.velocity_convention,
        ),
        model=Spectrum(
            spectral_axis=template_line.spectral_axis.copy(),
            flux=stacked_model * template_line.observed.unit,
            rest_value=template_line.rest_value.copy(),
            velocity_convention=template_line.model.velocity_convention,
        ),
    )
    return (line_stacked,)


@app.cell
def _(line_stacked, np, u):
    # Compute cross-correlation

    # Check same number of channels in all arrays:
    check_length_arrays = np.array([
        line_stacked.observed.flux.value,
        line_stacked.observed.spectral_axis.value,
        line_stacked.model.flux.value,
        line_stacked.model.spectral_axis.value,
    ])
    all_same_length = len(set(len(arr) for arr in check_length_arrays)) == 1
    n_chan = len(line_stacked.observed.flux.value) if all_same_length else None

    # Extract the physical velocity axis in km/s and model flux arrays
    v_axis = line_stacked.observed.spectral_axis.to(u.km / u.s).value
    model_flux = line_stacked.model.flux.value
    # Calculate the intensity-weighted center (centroid) of the model line (e.g., -3.1 km/s)
    v_center = np.sum(v_axis * model_flux) / np.sum(model_flux)
    # Get the relative channel spacing steps measured from the middle of the array
    relative_offsets = v_axis - v_axis[n_chan // 2]
    lags = relative_offsets
    # Anchor the lag axis to the centroid value instead of 0
    lags_shifted = relative_offsets + v_center


    ## Scipy FFT cross-correlation
    F_data = np.fft.fft(line_stacked.observed.flux.value)
    F_model = np.fft.fft(line_stacked.model.flux.value)
    corr = np.fft.ifft(F_data * np.conj(F_model)).real

    # Move zero-lag to the center of the array for the correlation data
    corr = np.fft.fftshift(corr)

    # Normalize correlation to S/N units
    corr /= np.std(corr)
    # corr /= (np.std(corr)**2)
    return corr, lags, v_center


@app.cell
def _(
    corr,
    lags,
    line_stacked,
    np,
    plt,
    use_custom_velocity_axes,
    v_center,
    v_ref,
):
    # Plot main results

    main_fig, main_fig_axes = plt.subplots(1, 2, figsize=(12,5))


    main_fig_axes[0].plot(line_stacked.spectral_axis, line_stacked.flux, drawstyle='steps-mid',
                    color='black', lw=2)
    main_fig_axes[0].plot(line_stacked.spectral_axis, line_stacked.model.flux,
                    color='red', lw=2)

    if use_custom_velocity_axes:
        main_fig_axes[0].axvline(v_ref, color='red', linestyle='--', alpha=0.7)
    main_fig_axes[0].grid(True, alpha=0.3)

    main_fig_axes[0].set_xlabel('Velocity (km/s)')
    main_fig_axes[0].set_ylabel('Flux / Intensity')
    main_fig_axes[0].set_title('Stacked Molecular Emission Lines')
    # main_fig_axes[0].set_xlim(-20, 20)
    main_fig_axes[0].set_ylim(-0.005, 0.0052)

    main_fig_axes[1].plot(lags, corr, color='black')
    main_fig_axes[1].set_xlabel("Velocity shift (km/s)")
    main_fig_axes[1].set_ylabel("S/N")
    main_fig_axes[1].set_title("Impulse response")
    # main_fig_axes[1].set_xlim(-20, 20)

    peak_shift = lags[np.argmax(corr)]

    # print(f"Peak correlation S/N            = {peak_sn:.2f}")
    print(f"Recovered shift               = {peak_shift:.3f} km/s")
    print(f"Line centroid                 = {v_center:.3f} km/s")
    # print(f"Detected velocity of first comp = {peak_vel:.3f} km/s")

    plt.tight_layout()
    return main_fig, peak_shift


@app.cell
def _(lines, model, plt, u, view_each_transition):
    # Plot individual lines

    if view_each_transition:

        figsize = (6, 8)
        lines_fig, lines_axes = plt.subplots(4, 1, figsize=figsize)

        for _ax, _line in zip(lines_axes, lines):

            _ax.plot(
                _line.spectral_axis.to(u.km/u.s),
                _line.flux,
                drawstyle="steps-mid",
                color="black",
                alpha=0.8,
            )
            _ax.plot(
                _line.spectral_axis.to(u.km/u.s),
                _line.model.flux,
                drawstyle="steps-mid",
                color="red",
            )

            # _ax.axvline(0.0, color="k", ls="--", alpha=0.5)

            _ax.set_ylabel("Intensity")
            _ax.set_xlabel("Velocity [km/s]")
            _ax.set_title("SLIM generated model over observed spectrum")
            _ax.text(
                0.02,
                0.98,
                f"{_line.rest_value}",
                ha="left",
                va="top",
                transform=_ax.transAxes,
            )

            _ax.set_xlim(-40, 40)
            _ax.set_ylim(-1.5 * model.max(), 2 * model.max())

        plt.tight_layout()
        # plt.savefig(f"{_line.rest_value}-mult.png", dpi=300)
    else:
        lines_fig = None
    return (lines_fig,)


if __name__ == "__main__":
    app.run()
