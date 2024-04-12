from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import pandas as pd

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_checkbox_group(
            id="ticks", label="Choose Tickers", choices=["a", "b", "c"]
        )
    ),
    ui.layout_columns(ui.card(ui.card_header("test"), ui.output_code("table"))),
    window_title="Market Tracker",
)


def server(input, output, session):
    pass

    @render.text
    def table():
        return input.ticks()


app = App(app_ui, server)
