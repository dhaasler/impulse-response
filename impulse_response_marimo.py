# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "astropy==8.0.1",
#     "marimo>=0.23.14",
#     "matplotlib==3.11.1",
#     "numpy==2.5.1",
#     "specutils==2.4.0",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(
    width="medium",
    app_title="Impulse Response",
    css_file="custom.css",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Impulse response
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # File pickers

    file_picker_SLIM = mo.ui.file(filetypes=[".csv"], kind="area")
    file_picker_spectra = mo.ui.file(multiple=True, kind="area")               

    files_layout = mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("### 📂 Select SLIM File"),
                    file_picker_SLIM,
                ]
            ),
            mo.vstack(
                [
                    mo.md("### 📂 Select Spectra File(s)"),
                    file_picker_spectra,
                ]
            ),
        ],
        widths="equal", # Makes both columns share equal width
        align="start",  # Keeps titles aligned at the top
    )

    # --- General & Units ---
    molecule_ui = mo.ui.text(value="PO,v=0", label="Molecule Formula")

    freq_units_list = ["GHz", "MHz", "kHz", "Hz"]
    flux_units_list = ["Jy", "mJy", "uJy", "K", "mK"]

    slim_freq_unit_ui = mo.ui.dropdown(
        options=freq_units_list, value="MHz", label="SLIM Frequency Unit"
    )
    spectra_freq_unit_ui = mo.ui.dropdown(
        options=freq_units_list, value="GHz", label="Spectra Frequency Unit"
    )
    spectra_flux_unit_ui = mo.ui.dropdown(
        options=flux_units_list, value="Jy", label="Spectra Flux Unit"
    )

    # Render
    mo.vstack([
        files_layout,
        mo.md("---"),
        mo.md("### 🏷️ Target molecule & Input units"),
        mo.hstack([
            slim_freq_unit_ui,
        ], justify="start", gap=2),
        mo.hstack([
            spectra_freq_unit_ui,
            spectra_flux_unit_ui,
        ], justify="start", gap=2)
    ])
    return (
        file_picker_SLIM,
        file_picker_spectra,
        slim_freq_unit_ui,
        spectra_flux_unit_ui,
        spectra_freq_unit_ui,
    )


@app.cell(hide_code=True)
def _(BytesIO, Table, file_picker_SLIM, mo):
    # The SLIM Gate: Stop immediately if the tuple is empty

    mo.stop(
        len(file_picker_SLIM.value) == 0,
        mo.md("### 👈 Please upload a SLIM file above to begin..."),
    )

    # 2. The Processing: This code will NEVER run unless a file is uploaded
    try:
        # Grab the raw byte contents of the first uploaded file
        slim_raw_bytes = file_picker_SLIM.contents(0)
        # Wrap the bytes into an in-memory virtual file stream
        slim_file = BytesIO(slim_raw_bytes)
        # Read the table
        slim_table = Table.read(slim_file, format="csv", delimiter=",")

    except Exception as e:
        mo.stop(True, mo.md(f"❌ **Error parsing SLIM file:** {str(e)}"))
    return (slim_table,)


@app.cell(hide_code=True)
def _(
    BytesIO,
    Spectrum,
    Table,
    file_picker_spectra,
    mo,
    spectra_flux_unit_ui,
    spectra_freq_unit_ui,
    u,
):
    # The Spectra Gate: Stop immediately if the tuple is empty

    mo.stop(
        len(file_picker_spectra.value) == 0,
        mo.md("### 👈 Please upload one or more spectrum files above to "
              "begin..."),
    )

    spectra_freq_unit = getattr(u, spectra_freq_unit_ui.value)
    spectra_flux_unit = getattr(u, spectra_flux_unit_ui.value)

    # 2. The Processing: This code will NEVER run unless a file is uploaded
    try:
        # Read every file as a virtual file stream
        spectra_filenames = [
            BytesIO(file_picker_spectra.contents(i))
            for i in range(len(file_picker_spectra.value))
        ]
        # Store Spectrum and Table just in case.
        spectra_tables = []
        spectra = []
        for filename in spectra_filenames:
            spectrum_table = Table.read(filename, format="ascii")
            spectra_tables.append(spectrum_table)
            spectra.append(
                Spectrum(
                    spectral_axis=spectrum_table.columns[0].data
                    * spectra_freq_unit,
                    flux=spectrum_table.columns[1].data * spectra_flux_unit,
                )
            )

    except Exception as e:
        mo.stop(True, mo.md(f"❌ **Error parsing spectrum file:** {str(e)}"))
    return spectra, spectra_flux_unit


@app.cell(hide_code=True)
def _(dataset_mols_selector_ui, mo):
    # Build the conditional UI section for molecule selection

    mo.vstack(
        [
            mo.md("### Molecule"),
            mo.hstack(
                [
                    dataset_mols_selector_ui,
                ],
                justify="start",
                gap=3,
            ),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(
    channel_width_ui,
    mo,
    ref_vel_ui,
    resample_method_ui,
    use_custom_velocity_axes_ui,
):
    # Build the conditional UI section for custom velocity axes

    if use_custom_velocity_axes_ui.value:
        custom_axes_controls = mo.hstack(
            [ref_vel_ui, channel_width_ui],
            gap=1
        )
        velocity_section = mo.vstack(
            [use_custom_velocity_axes_ui, custom_axes_controls]
        )
    else:
        velocity_section = use_custom_velocity_axes_ui

    # Display controls in two balanced columns
    mo.vstack(
        [
            mo.md("### Resampling"),
            mo.hstack(
                [
                    resample_method_ui,
                    velocity_section,
                ],
                justify="start",
                gap=3,
            ),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(
    baseline_window_ui,
    custom_freqs_text_ui,
    dataset_freq_selector_ui,
    mo,
    stack_weighting_ui,
    stacking_freqs_unit_ui,
    stacking_mode_ui,
    stacking_window_ui,
):
    # Build the conditional UI section for transitions selection

    # Dynamic section for transitions selection
    if stacking_mode_ui.value == "Select from dataset":
        stacking_freq_section = dataset_freq_selector_ui
    elif stacking_mode_ui.value == "Custom list":
        stacking_freq_section = mo.vstack(
            [stacking_freqs_unit_ui, custom_freqs_text_ui],
            gap=1
        )
    else:
        stacking_freq_section = mo.md("_Using all detected transitions from dataset._")

    # Display controls in two balanced columns
    mo.vstack(
        [
            mo.md("### Stacking"),
            mo.hstack(
                [
                    stack_weighting_ui,
                    stacking_window_ui,
                ],
                justify="start",
                gap=3,
            ),
            baseline_window_ui,
            stacking_mode_ui,
            stacking_freq_section,
            # mo.md("### Extra"),
            # view_each_transition_ui,
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(lines_fig, main_fig, mo, peak_shift, v_center):
    # Show results

    main_view = mo.vstack(
        [
            mo.md("# Impulse Response results"),
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
                        mo.md(
                            "Detailed plot showing each spectrum used in the "
                            "impulse response calculation:"
                        ),
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Hidden (seriously, don't look)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imports and aux functions
    """)
    return


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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

            resampled_observed = resampler(self.observed, new_axis)
            resampled_model = resampler(self.model, new_axis)

            # First velocity convention has to be set, then the rest_value
            # setter. Limitations of how Spectrum works
            if hasattr(self.observed, "velocity_convention"):
                resampled_observed = (
                    resampled_observed.with_velocity_convention(
                        self.observed.velocity_convention
                    )
                )
                resampled_model = resampled_model.with_velocity_convention(
                    self.model.velocity_convention
                )
            if hasattr(self.observed, "rest_value"):
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
        return intensity * np.exp(
            -((vel_array - velocity) ** 2) / (2 * sigma**2)
        )

    def round_up_to_even(f):
        return np.ceil(f / 2.) * 2

    return LineSpectrum, gaussian_profile, round_up_to_even


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## UI preparation
    """)
    return


@app.cell(hide_code=True)
def _(np, slim_freq_unit_ui, slim_table, spectra, u):
    # Read SLIM and spec data to get the frequencies inside both input files
    # before setting the rest of the UI.

    # Set SLIM data
    slim_freq_unit = getattr(u, slim_freq_unit_ui.value)
    slim_table["Frequency"].unit = slim_freq_unit

    # Get every line inside SLIM and spectra
    freq_range_filter = np.zeros(len(slim_table), dtype=bool)
    for _spectrum in spectra:
        spec_freq = _spectrum.spectral_axis
        freq_range_filter |= (slim_table["Frequency"] > spec_freq.min()) & (
            slim_table["Frequency"] < spec_freq.max()
        )
    slim_table_freq = slim_table[freq_range_filter]

    # Show to which molecules belong the transitions contained in the SLIM and
    # spectra files
    mols = sorted(np.unique(slim_table_freq["Formula"]))
    return freq_range_filter, mols


@app.cell(hide_code=True)
def _(dataset_mols_selector_ui, freq_range_filter, np, slim_table):
    # Read the user selected molecule to get the frequencies of said molecule
    # and show it to the user to select transitions

    # molecule = molecule_ui.value
    molecule = dataset_mols_selector_ui.value
    molecule_filter = slim_table["Formula"] == molecule
    slim_table_mol_freq = slim_table[freq_range_filter & molecule_filter]
    freqs = sorted(np.unique(slim_table_mol_freq["Frequency"]))
    return freqs, slim_table_mol_freq


@app.cell(hide_code=True)
def _(mo, mols):
    # Post upload processing #1: Show molecules found in all input 

    mol_options = [str(m) for m in mols]
    dataset_mols_selector_ui = mo.ui.dropdown(
        options=mol_options,
        value=mol_options[0],
        label="Select Transitions from Dataset",
    )
    return (dataset_mols_selector_ui,)


@app.cell(hide_code=True)
def _(mo):
    # Post-upload processing #2 of controls for secondary UI

    # --- Stacking & Resampling ---
    stack_weighting_ui = mo.ui.dropdown(
        options=["equal", "sigma"], value="sigma", label="Stacking weight"
    )
    resample_method_ui = mo.ui.dropdown(
        options=["linear", "flux conserving"],
        value="flux conserving",
        label="Resample method"
    )

    use_custom_velocity_axes_ui = mo.ui.switch(
        label="Use custom velocity axes"
    )
    ref_vel_ui = mo.ui.number(value=0, label="Ref Vel (km/s)")
    channel_width_ui = mo.ui.number(value=1, label="Channel Width (km/s)")
    return (
        channel_width_ui,
        ref_vel_ui,
        resample_method_ui,
        stack_weighting_ui,
        use_custom_velocity_axes_ui,
    )


@app.cell(hide_code=True)
def _(freqs, mo):
    # Post-upload processing #3 of controls for secondary UI

    # --- Windows ---

    # Option A: Dual-thumb range slider
    stacking_window_ui = mo.ui.range_slider(
        start=-100,
        stop=100,
        value=[-60, 60],
        step=1,
        show_value=True,
        label="Stacking Window Vel (km/s)",
    )

    # Option B: Number inputs arranged horizontally
    # (Best for exact numerical entry)
    baseline_window_ui = mo.md(
        """
        Baseline Window Vel (km/s): 
        {min_vel} to {max_vel}
        """
    ).batch(
        min_vel=mo.ui.number(value=-1, label="Min"),
        max_vel=mo.ui.number(value=1, label="Max"),
    )



    # --- Transitions / Frequencies Selection ---
    stacking_mode_ui = mo.ui.dropdown(
        options=["All", "Select from dataset", "Custom list"],
        value="All",
        label="Transitions to Stack"
    )
    freq_options = [str(f) for f in freqs]
    dataset_freq_selector_ui = mo.ui.multiselect(
        options=freq_options,
        value=freq_options,
        label="Select Transitions from Dataset",
    )
    custom_freqs_text_ui = mo.ui.text_area(
        value="152656.979, 152680.282, 152855.454",
        placeholder="152656.979, 152680.282"
    )
    stacking_freqs_unit_ui = mo.ui.dropdown(
        options=["MHz", "GHz", "kHz", "Hz"],
        value="MHz",
        label="Enter Frequencies separated by commas or newlines. Unit: "
    )

    # Logging
    view_each_transition_ui = mo.ui.checkbox(value=True, label="View each transition")
    return (
        baseline_window_ui,
        custom_freqs_text_ui,
        dataset_freq_selector_ui,
        stacking_freqs_unit_ui,
        stacking_mode_ui,
        stacking_window_ui,
        view_each_transition_ui,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Main program code
    """)
    return


@app.cell(hide_code=True)
def _():
    # (COMMENTED CELL) Data preparation #1 (moved to top of the notebook
    # before setting UI)

    # SLIM and Spectra preparation

    # Moved to cell on top for notebook
    # slim_table = Table.read(slim_filename, format='csv', delimiter=",")  
    # slim_table["Frequency"].unit = slim_freq_unit
    # Molecule filter
    # molecule_filter = slim_table["Formula"] == molecule

    # # Frequency filter
    # # Moved to cell on top for notebook
    # # Store Spectrum and Table just in case.
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

    # freq_range_filter = np.zeros(len(slim_table), dtype=bool)
    # for _spectrum in spectra:
    #     spec_freq = _spectrum.spectral_axis
    #     freq_range_filter |= (slim_table["Frequency"] > spec_freq.min()) & (
    #         slim_table["Frequency"] < spec_freq.max()
    #     )
    # slim_table_mol_freq = slim_table[molecule_filter & freq_range_filter]
    # freqs = sorted(np.unique(slim_table_mol_freq["Frequency"]))
    return


@app.cell(hide_code=True)
def _():
    # # (COMMENTED CELL) User input (script version)

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

    # resample_method = 'linear'  # 'linear' (default) or 'flux conserving' (CLASS)

    # # Logging
    # view_each_transition = True
    return


@app.cell(hide_code=True)
def _(
    baseline_window_ui,
    channel_width_ui,
    ref_vel_ui,
    resample_method_ui,
    stack_weighting_ui,
    stacking_window_ui,
    use_custom_velocity_axes_ui,
    view_each_transition_ui,
):
    # Read parameters (marimo notebook version)

    # Stacking parameters

    stacking_weighting = stack_weighting_ui.value

    # Extract range_slider values
    stacking_window_params = {
        "min_vel": stacking_window_ui.value[0],
        "max_vel": stacking_window_ui.value[1],
    }

    # Extract dictionary values
    baseline_window_params = {
        "min_vel": baseline_window_ui.value["min_vel"],
        "max_vel": baseline_window_ui.value["max_vel"],
    }

    # Resampling parameters

    # If False, the program uses the velocity array for the first line and
    # custom_velocity_axes_params are ignored:
    use_custom_velocity_axes = use_custom_velocity_axes_ui.value
    # If use_custom_velocity_axes is True:
    # Extract custom velocity parameters safely
    if use_custom_velocity_axes_ui.value:
        custom_velocity_axes_params = {
            "ref_vel": ref_vel_ui.value,
            "channel_width": channel_width_ui.value,
        }
    else:
        custom_velocity_axes_params = None

    resample_method = resample_method_ui.value

    # Logging
    view_each_transition = view_each_transition_ui.value
    return (
        custom_velocity_axes_params,
        resample_method,
        stacking_weighting,
        stacking_window_params,
        use_custom_velocity_axes,
        view_each_transition,
    )


@app.cell(hide_code=True)
def _(
    custom_freqs_text_ui,
    dataset_freq_selector_ui,
    freqs,
    np,
    slim_freq_unit_ui,
    slim_table_mol_freq,
    stacking_freqs_unit_ui,
    stacking_mode_ui,
    u,
):
    # Filter line data selected for stacking

    if stacking_mode_ui.value == "All":
        # Use every transition available from the input table/spectrum
        selected_stacking_freqs = freqs
        selected_stacking_unit = slim_freq_unit_ui.value
    elif stacking_mode_ui.value == "Select from dataset":
        # Convert chosen multiselect string items back to float numbers
        selected_stacking_freqs = [
            float(f) for f in dataset_freq_selector_ui.value
        ]
        selected_stacking_unit = slim_freq_unit_ui.value
    elif stacking_mode_ui.value == "Custom list":
        # Parse raw text box input (handles commas, spaces, or newlines)
        raw_text = custom_freqs_text_ui.value
        # Replace newlines with commas, split on comma, and clean whitespace
        cleaned_items = raw_text.replace("\n", ",").split(",")
        selected_stacking_freqs = [
            float(item.strip()) for item in cleaned_items if item.strip()
        ]
        selected_stacking_unit = stacking_freqs_unit_ui.value
    # Convert the unit string to astropy unit object
    stacking_freqs_unit = getattr(u, selected_stacking_unit)

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


@app.cell(hide_code=True)
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

    group_col = (
        "Transition"
        if "Transition" in slim_table_stacking.colnames
        else "Frequency"
    )
    slim_table_stacking_grouped = slim_table_stacking.group_by(group_col)

    lines = []
    for key, group in zip(
        slim_table_stacking_grouped.groups.keys,
        slim_table_stacking_grouped.groups,
    ):
        # Here group is each transition table of the molecule

        # Rest frequency of this transition
        rest_freq = group["Frequency"].quantity[0]

        # Check if all rows are the same transition
        group_freqs = group["Frequency"].quantity
        if "Transition" in group.colnames:
            if not np.all(group["Transition"] == group["Transition"][0]):
                raise ValueError(
                    f"Transitions check failed: they differ between "
                    "velocity components"
                )
        elif not np.allclose(
            group_freqs.to_value(u.MHz),
            group_freqs[1].to_value(u.MHz),
            rtol=1e-12,
            atol=1e-12,
        ):  # This has precision up to the Hz on MHz arrays
            raise ValueError(
                f"Transitions check failed: they differ between "
                "velocity components"
            )

        component_lines = np.column_stack(
            [
                group["Intensity"],
                group["Velocity"],
                group["Width"],
            ]
        )

        for _spectrum in spectra:
            # Check if transition is inside this spectrum
            if not (
                _spectrum.spectral_axis.min()
                <= rest_freq
                <= _spectrum.spectral_axis.max()
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
                model += gaussian_profile(
                    spec_vel_value, intensity, vel, width
                )

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
                f"Transition at {rest_freq} was not found in any selected "
                "spectrum."
            )
    return (lines,)


@app.cell(hide_code=True)
def _(
    custom_velocity_axes_params,
    lines,
    np,
    stacking_window_params,
    u,
    use_custom_velocity_axes,
):
    # Prepare common velocity axis

    v_min = stacking_window_params["min_vel"]
    v_max = stacking_window_params["max_vel"]

    # Prepare slices common velocity axes
    if use_custom_velocity_axes == True:
        # Custom velocity axis with vref in the middle of its channel
        dv = custom_velocity_axes_params["channel_width"]
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
        common_velocity_value = lines[0].spectral_axis.to(u.km / u.s).value
        slice_mask = ((common_velocity_value >= v_min) & 
                      (common_velocity_value <= v_max))
        common_velocity = common_velocity_value[slice_mask]
        # If the axis was in frequency, we need to swap its order so that the
        # velocity array is incremental
        if common_velocity[0] > common_velocity[-1]:
            common_velocity = common_velocity[::-1]

    resample_velocity = common_velocity * u.km / u.s
    return resample_velocity, v_max, v_min, v_ref


@app.cell(hide_code=True)
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
        extrapolation_treatment="nan_fill"
    )
    flux_conserving_resampler = FluxConservingResampler(
        extrapolation_treatment="nan_fill"
    )

    lines_resampled = []
    # Slice spectra around each line and resample them to the common velocity
    # axis
    for _line in lines:
        _v_slice = _line.spectral_axis.to(u.km / u.s).value.copy()

        # Interpolate the data onto the common velocity grid slice
        # Ensure the velocity axis is strictly increasing for resampling
        # Ensure increasing velocity axis
        if len(_v_slice) > 1 and _v_slice[0] > _v_slice[-1]:
            current_line = _line.reverse()
        else:
            current_line = _line

        # Resample line
        if resample_method == "linear":
            line_resampled = current_line.to_vel().resample(
                linear_resampler, resample_velocity
            )
        elif resample_method == "flux conserving":
            line_resampled = current_line.to_vel().resample(
                flux_conserving_resampler, resample_velocity
            )

        # Store resampled lines
        lines_resampled.append(line_resampled)
    return (lines_resampled,)


@app.cell(hide_code=True)
def _(
    LineSpectrum,
    Spectrum,
    baseline_window_ui,
    lines_resampled,
    np,
    u,
    v_max,
    v_min,
):
    # Apply baseline to each line

    lines_resampled_baselined = []
    for _line in lines_resampled:
        _f_slice = _line.observed.flux.value.copy()
        _v_slice = _line.observed.spectral_axis.to(u.km / u.s).value.copy()

        # Baseline each slice before stacking to allow sigma based weighting
        # Define your window boundaries for the baseline
        base_min = baseline_window_ui["min_vel"].value
        base_max = baseline_window_ui["max_vel"].value
        # Create a mask specifically matching the baseline region on the
        # common grid
        baseline_mask = (
            ((_v_slice >= v_min) & (_v_slice <= base_min)) |
            ((_v_slice <= v_max) & (_v_slice >= base_max))
        )
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
    return base_max, base_min, lines_resampled_baselined


@app.cell(hide_code=True)
def _(
    LineSpectrum,
    Spectrum,
    lines_resampled_baselined,
    np,
    spectra_flux_unit,
    stacking_weighting,
):
    # Stack the spectra and model

    obs_slices = [
        _line.observed.flux.to(spectra_flux_unit).value.copy()
        for _line in lines_resampled_baselined
    ]
    model_slices = [
        _line.model.flux.to(spectra_flux_unit).value.copy()
        for _line in lines_resampled_baselined
    ]

    if stacking_weighting == "equal":
        weights = None
    elif stacking_weighting == "sigma":
        std_devs = [
            np.std(slice) for slice in obs_slices
        ]  # estimate noise from slice
        weights = 1.0 / np.array(std_devs) ** 2
    else:
        weights = None

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


@app.cell(hide_code=True)
def _(line_stacked, np, u):
    # Compute cross-correlation

    # Check same number of channels in all arrays:
    check_length_arrays = np.array(
        [
            line_stacked.observed.flux.value,
            line_stacked.observed.spectral_axis.value,
            line_stacked.model.flux.value,
            line_stacked.model.spectral_axis.value,
        ]
    )
    all_same_length = len(set(len(arr) for arr in check_length_arrays)) == 1
    n_chan = len(line_stacked.observed.flux.value) if all_same_length else None

    # Extract the physical velocity axis in km/s and model flux arrays
    v_axis = line_stacked.observed.spectral_axis.to(u.km / u.s).value
    model_flux = line_stacked.model.flux.value
    # Calculate the intensity-weighted center (centroid) of the model line
    v_center = np.sum(v_axis * model_flux) / np.sum(model_flux)
    # Get the relative channel spacing steps measured from the middle of the
    # array
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


@app.cell(hide_code=True)
def _(
    base_max,
    base_min,
    corr,
    lags,
    line_stacked,
    np,
    plt,
    use_custom_velocity_axes,
    v_max,
    v_min,
    v_ref,
):
    # Create plot for main results

    main_fig, main_fig_axes = plt.subplots(1, 2, figsize=(10, 4.5))

    main_fig_axes[0].plot(
        line_stacked.spectral_axis,
        line_stacked.flux,
        drawstyle="steps-mid",
        color="black",
        lw=2,
    )
    main_fig_axes[0].plot(
        line_stacked.spectral_axis, line_stacked.model.flux, color="red", lw=2
    )

    if use_custom_velocity_axes:
        main_fig_axes[0].axvline(v_ref, color="red", linestyle="--", alpha=0.7)
    main_fig_axes[0].grid(True, alpha=0.3)

    _y_lim = main_fig_axes[0].get_ylim()
    main_fig_axes[0].plot(
        (v_min, base_min),
        (0.75 * (_y_lim[1] - _y_lim[0]), 0.75 * (_y_lim[1] - _y_lim[0])),
        color="blue",
    )
    main_fig_axes[0].plot(
        (base_max, v_max),
        (0.75 * (_y_lim[1] - _y_lim[0]), 0.75 * (_y_lim[1] - _y_lim[0])),
        color="blue",
    )

    main_fig_axes[0].set_xlabel("Velocity (km/s)")
    main_fig_axes[0].set_ylabel("Flux / Intensity")
    main_fig_axes[0].set_title("Stacked Molecular Emission Lines")
    # main_fig_axes[0].set_xlim(-20, 20)
    # main_fig_axes[0].set_ylim(-0.005, 0.0052)

    main_fig_axes[1].plot(lags, corr, color="black")
    main_fig_axes[1].set_xlabel("Velocity shift (km/s)")
    main_fig_axes[1].set_ylabel("S/N")
    main_fig_axes[1].set_title("Impulse response")
    # main_fig_axes[1].set_xlim(-20, 20)

    peak_shift = lags[np.argmax(corr)]

    plt.tight_layout()
    return main_fig, peak_shift


@app.cell(hide_code=True)
def _(lines, np, plt, round_up_to_even, u, v_max, v_min, view_each_transition):
    # Create plot for individual lines

    if view_each_transition:

        _n_plots = len(lines)

        figsize = (7, 1.5*round_up_to_even(_n_plots))
        _rows = int(np.ceil(_n_plots/2))
        lines_fig, lines_axes = plt.subplots(_rows, 2, figsize=figsize)

        for _ax, _line in zip(lines_axes.flatten(), lines):
            _ax.plot(
                _line.spectral_axis.to(u.km / u.s),
                _line.flux,
                drawstyle="steps-mid",
                color="black",
                alpha=0.8,
            )
            _ax.plot(
                _line.spectral_axis.to(u.km / u.s),
                _line.model.flux,
                drawstyle="steps-mid",
                color="red",
            )

            _ax.set_ylabel("Intensity")
            _ax.set_xlabel("Velocity [km/s]")
            # _ax.set_title("SLIM generated model over observed spectrum")
            _ax.text(
                0.02,
                0.98,
                f"{_line.rest_value}",
                ha="left",
                va="top",
                transform=_ax.transAxes,
            )

            # Plot limits
            _ax.set_xlim(v_min, v_max)
            stacking_window_mask = (
                (_line.spectral_axis.to(u.km / u.s).value > v_min) &
                (_line.spectral_axis.to(u.km / u.s).value < v_max)
            )
            _y_lims = (
                1.2 * _line.flux.value[stacking_window_mask].min(),
                1.2 * _line.flux.value[stacking_window_mask].max()
            )
            _ax.set_ylim(_y_lims)

        plt.tight_layout()
        # plt.savefig(f"{_line.rest_value}-mult.png", dpi=300)
    else:
        lines_fig = None
    return (lines_fig,)


if __name__ == "__main__":
    app.run()
