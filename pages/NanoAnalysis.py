import calendar
import tempfile
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import os
import sys
import mvexperiment.experiment as experiment
import numpy as np
import zipfile
import matplotlib.pyplot as plt
import pandas as pd
import json
import shutil
import altair as alt
import nanodata
import nanodata.nanodata as nano
from NanoPrepare import save_uploaded_file, base_chart, layer_charts
import nanoanalysisdata.engine as engine


def handle_click(i: int) -> None:
    # activate and deactivate curve in haystack on checkbox click
    if engine.haystack[i].active:
        engine.haystack[i].active = False
    else:
        engine.haystack[i].active = True


def generate_raw_curves(haystack: list) -> list:
    all_curves = []
    for curve in haystack:
        if curve.active:
            df = pd.DataFrame(
                {
                    "z": curve.data["Z"],
                    "f": curve.data["F"],
                }
            )
            all_curves.append(df)
    return all_curves


def main() -> None:
    st.set_page_config(
        layout="wide", page_title="NanoWeb", page_icon="/images/cellmech.png"
    )

    top_bar = st.container()
    file = top_bar.file_uploader("Upload a JSON file")

    graph_bar = st.container()
    graph_first_col, graph_second_col, graph_third_col, graph_fourth_col = graph_bar.columns(4)

    filter_bar = st.container()
    filter_bar.write("Global Config")
    filter_first_col, filter_second_col, filter_third_col, filter_fourth_col, filter_fifth_col = filter_bar.columns(5)

    if file is not None:
        if file.name.endswith(".json"):
            save_uploaded_file(file, "data")

            # Load the JSON file
            f = open("data/" + file.name, "r")
            structure = json.load(f)
            # st.write(structure)

            for cv in structure["curves"]:
                engine.haystack.append(engine.curve(cv))

            # File selection checkboxes
            graph_first_col.write("Files")

            for i, curve in enumerate(engine.haystack):
                graph_first_col.checkbox(curve.filename, value=True, key=i, on_change=handle_click, args=(i,))

            # Raw curve plot
            graph_second_col_raw = graph_second_col.container()
            graph_second_col_raw.write("Raw curves")
            graph_second_col_raw_plot = graph_second_col_raw.line_chart()
            raw_curves = generate_raw_curves(engine.haystack)

            graph_second_col_raw_plot.altair_chart(
                layer_charts(raw_curves, base_chart),
                use_container_width=True
            )

            # Current curve plot
            graph_second_col_current = graph_second_col.container()
            graph_second_col_current.write("Current curve")
            options = [curve.filename for curve in engine.haystack if curve.active]
            selected_index = options.index(graph_second_col_current.selectbox('Select a curve', options, index=0))
            graph_second_col_current_plot = graph_second_col_current.line_chart()

            graph_second_col_current_plot.altair_chart(
                base_chart(raw_curves[selected_index]),
                use_container_width=True
            )

            # Hertz analysis
            hertz_active = graph_third_col.checkbox("Hertz Analysis")
            if hertz_active:
                graph_third_col_indent = graph_third_col.container()
                graph_third_col_indent.write("Indentation curves")
                graph_third_col_indent_plot = graph_third_col_indent.line_chart()

                graph_third_col_f_ind = graph_third_col.container()
                graph_third_col_f_ind.write("Average F-ind")
                graph_third_col_f_ind_plot = graph_third_col_f_ind.line_chart()

                graph_third_col_elasticity = graph_third_col.container()
                graph_third_col_elasticity.write("Elasticity values")
                graph_third_col_elasticity_plot = graph_third_col_elasticity.line_chart()

            # Elasticity Spectra analysis
            el_spec_active = graph_fourth_col.checkbox("Elasticity Spectra Analysis")
            if el_spec_active:
                graph_fourth_col_el_spec = graph_fourth_col.container()
                graph_fourth_col_el_spec.write("Elasticity Spectra")
                graph_fourth_col_el_spec_plot = graph_fourth_col_el_spec.line_chart()

                graph_fourth_col_bilayer = graph_fourth_col.container()
                graph_fourth_col_bilayer.write("Bilayer model")
                graph_fourth_col_bilayer_plot = graph_fourth_col_bilayer.line_chart()

        else:
            st.warning("Only files with the .json extension are supported.")


if __name__ == "__main__":
    main()
