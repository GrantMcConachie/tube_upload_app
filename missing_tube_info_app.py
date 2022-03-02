import dash
from dash import html
from dash import dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, ALL, State
import webbrowser
import csv
from datetime import datetime
from pathlib import Path
from itertools import chain
import pandas as pd
import requests

"""Global Variables"""


result_data_dir = ".\\Test Result Data\\"


"""Functions"""


def read_csvs(result_data_dir):
    """Goes through the last week of grossFINAL and tareFINAL csvs and checks if there is missing info"""
    fifty_days = 95378.95542693138 * 50  # seconds
    fifty_days_ago = datetime.now().timestamp() - fifty_days  # seconds
    table_rows = []
    update_info = []

    for path in chain(
        Path(result_data_dir).rglob("*tareFINAL.csv"),
        Path(result_data_dir).rglob("*grossFINAL.csv"),
    ):
        file_creation_time = path.stat().st_mtime
        filename = str(path).split("\\")[-1]

        # Changed the key dependng on gross or tare file
        if "tareFINAL.csv" in filename:
            col_key = "Src2D"
        elif "grossFINAL.csv" in filename:
            col_key = "Tgt2D"

        # Determines if the file was made within the last week
        if file_creation_time > fifty_days_ago:
            # To get barcode underneath
            df = pd.read_csv(path)
            df = df.append([""], ignore_index=True)

            with open(path, newline="") as csvfile:
                spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")

                # Goes through the rows of the CSV finds missing things
                for i, row in enumerate(spamreader):
                    if row[2] == "NOREAD" or row[2] == "":
                        table_rows.append(
                            html.Tr(
                                [
                                    html.Th(row[0]),
                                    html.Th(row[1]),
                                    html.Th("Barcode"),
                                    html.Th(df.iloc[i][col_key]),
                                    html.Th(
                                        [
                                            dcc.Input(
                                                id={
                                                    "type": "input",
                                                    "index": "input"
                                                    + filename
                                                    + row[1]
                                                    + "barcode",
                                                },
                                                type="text",
                                                style={"text-align": "left"},
                                            ),
                                            html.Button(
                                                "Upload",
                                                id={
                                                    "type": "button",
                                                    "index": filename
                                                    + row[1]
                                                    + "barcode",
                                                },
                                                style={"margin-left": "5px"},
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        )
                        update_info.append([filename, i, 2])

                    if row[3] == "":
                        table_rows.append(
                            html.Tr(
                                [
                                    html.Th(row[0]),
                                    html.Th(row[1]),
                                    html.Th("Weight"),
                                    html.Th(df.iloc[i]["Src2D"]),
                                    html.Th(
                                        [
                                            dcc.Input(
                                                id={
                                                    "type": "input",
                                                    "index": "input"
                                                    + filename
                                                    + row[1]
                                                    + "weight",
                                                },
                                                type="text",
                                                style={"text-align": "left"},
                                            ),
                                            html.Button(
                                                "Upload",
                                                id={
                                                    "type": "button",
                                                    "index": filename
                                                    + row[1]
                                                    + "weight",
                                                },
                                                style={"margin-left": "5px"},
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        )
                        update_info.append([filename, i, 3])

    return table_rows, update_info


def serve_layout():
    """Keeps table up to date on refresh"""
    global table_rows
    global update_info
    global table_header
    table_rows, update_info = read_csvs(result_data_dir)
    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Rack"),
                    html.Th("Tube"),
                    html.Th("Missing Info"),
                    html.Th("Tube Barcode Below"),
                    html.Th("Input"),
                ]
            )
        )
    ]
    table_body = [html.Tbody(table_rows)]
    table = dbc.Table(
        table_header + table_body, id="table", striped=True, bordered=True, hover=True
    )
    header = html.H1("Missing Tube info", id="test-output")
    loader = dbc.Spinner(html.Div("", id="spinner"))
    modal = html.Div(
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Fail")),
                dbc.ModalBody("Unable to upload"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)
                ),
            ],
            id="modal",
            is_open=False,
        )
    )

    return dbc.Container([header, table, loader, modal])


def change_csv(result_data_dir, filename, row_num, col_num, input):
    """Changes the csv: adds the 'input' variable to 'filename' in 'row_num','col_num'"""
    # Read CSV
    rows = []
    with open(result_data_dir + filename, newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            rows.append(row)
        csvfile.close()

    # Update CSV
    for j, row in enumerate(rows):
        if j == row_num:
            row[col_num] = input

    # Write CSV
    with open(result_data_dir + filename, "w", newline="") as csvfile:
        spamwriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        spamwriter.writerows(rows)
        csvfile.close()


"""App creation"""


app = dash.Dash(__name__)

# Serving locally
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# Creating app
app.layout = serve_layout


"""Callbacks"""


@app.callback(
    Output("table", "children"),
    Output("test-output", "children"),
    Output("spinner", "children"),
    Output("modal", "is_open"),
    Input({"type": "button", "index": ALL}, "n_clicks"),
    Input("close", "n_clicks"),
    State({"type": "input", "index": ALL}, "value"),
)
def on_click(n, close_modal, missing_info):
    for i, clicks in enumerate(n):
        if clicks != None:
            filename = update_info[i][0]
            row_num = update_info[i][1]
            col_num = update_info[i][2]
            input = missing_info[i]

            # Checking input
            if input is None:
                raise PreventUpdate
            else:
                # Adding input to CSV
                change_csv(result_data_dir, filename, row_num, col_num, input)

                # Upload CSV and check if successful
                with open(result_data_dir + filename, "r") as file:
                    file_string = file.read()
                    if "tareFINAL" in filename:
                        try:
                            resp = requests.post(
                                "path/to/database", 
                                data=file_string,
                                headers={'processData': 'false', 'Content-Type': 'text/plain'}
                            )

                        except:
                            change_csv(result_data_dir, filename, row_num, col_num, '')

                    elif "grossFINAL" in filename:
                        try:
                            resp = requests.post(
                                "path/to/database",
                                data=file_string,
                                headers={'processData': 'false', 'Content-Type': 'text/plain'}
                            )

                        except:
                            change_csv(result_data_dir, filename, row_num, col_num, '')

                # Update Table
                table_rows, _ = read_csvs(result_data_dir)
                if len(table_rows) == len(update_info):
                    return (
                        table_header + [html.Tbody(table_rows)],
                        "Missing Tube Info",
                        "",
                        True,
                    )
                else:
                    update_info.pop(i)
                    return (
                        table_header + [html.Tbody(table_rows)],
                        "Missing Tube Info",
                        "",
                        False,
                    )

        else:
            continue

    # Closes modal
    if close_modal:
        table_rows, _ = read_csvs(result_data_dir)
        return table_header + [html.Tbody(table_rows)], "Missing Tube Info", "", False

    raise PreventUpdate


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8050/")
    app.run_server(debug=False)
