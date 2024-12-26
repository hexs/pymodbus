from pprint import pprint
from flask import Flask, render_template, jsonify, request
from prettydf import column_mapping, read_p_df, write_p_df
import pandas as pd

app = Flask(__name__)


@app.route("/")
def show_table():
    return render_template("table_editor.html")


@app.route("/data", methods=["GET"])
def get_data():
    try:
        return jsonify(read_p_df())
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/save", methods=["POST"])
def save_changes():
    # try:
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
    p_df = pd.DataFrame(data)
    p_df.rename(columns=dict(zip(range(len(column_mapping)), column_mapping.keys())), inplace=True)
    write_p_df(p_df)
    return jsonify({"success": True}), 200

    # except Exception as e:
    #     return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
