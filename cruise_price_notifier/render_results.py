import datetime
import json
import csv
import sys
from datetime import datetime
import logging

log = logging.getLogger(__name__)


def read_json_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def write_to_csv(csv_file):
    data = read_json_from_file("resources/output.json")
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        try:
            for cruise in data:
                cruise['cruise_destinations'] = ', '.join(cruise['cruise_destinations'])
                writer.writerow(cruise)
        except Exception as e:
            log.error(str(e))


def sort_cruises_by_suite_price(cruises, field):
    def suite_price_key(cruise):
        try:
            return int(cruise[field].replace('€', '').replace(',', ''))
        except ValueError:
            return float('inf')

    return sorted(cruises, key=suite_price_key)


def sort_cruises_by_suite_price2(cruises):
    return sorted(cruises, key=lambda x: int(x["Suite"].replace('€', '').replace(',', '')))


def format_date():
    today = datetime.today()
    day = today.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    formatted_date = today.strftime(f"%B {day}{suffix} %Y")
    return formatted_date


def create_html_from_results(headers, field):
    cruises = read_json_from_file("resources/output.json")
    # remove all cruises where the headers are not in english / corrupted
    filtered_cruises = [m for m in cruises if all(key in m for key in headers)]
    sorted_cruises = sort_cruises_by_suite_price(filtered_cruises, field)
    if not sorted_cruises:
        log.error("Error sorting cruises. Shutting down.")
        sys.exit(0)
    room_types = ''.join([f'<th>{header} (€)</th>' for header in headers])

    today = format_date()

    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cruise Information {today}</title>
        <style>
            body {{
                font-family: Courier, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f9;
                color: #333;
            }}
            h1 {{
                text-align: center;
                background-color: #0270a7;
                color: white;
                padding: 20px;
                margin: 0 0 20px 0;
                border-radius: 8px;
            }}
            h4 {{
                text-align: center;
                background-color: #0270a7;
                color: white;
                padding: 20px;
                margin: 0 0 20px 0;
                border-radius: 8px;
            }}
            table {{
                width: 100%;
                margin: 0 auto;
                border-collapse: collapse;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px 15px;
                text-align: left;
            }}
            th {{
                background-color: #0270a7;
                color: white;
                cursor: pointer;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #e0e0e0;
            }}
            a {{
                color: #0270a7;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            @media (max-width: 600px) {{
                table {{
                    width: 100%;
                    display: block;
                    overflow-x: auto;
                }}
                th, td {{
                    white-space: nowrap;
                }}
            }}
        </style>
        <script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>
    </head>
    <body>
        <h1>Cruise Information {today}</h1>
        <h4>Sorted By {field} price (low to high)</h4>
        <table class="sortable">
            <thead>
                <tr>
                    <th>Ship</th>
                    <th>Duration</th>
                    <th>Destinations</th>
                    {room_types}
                    <th>URL</th>
                </tr>
            </thead>
            <tbody>
    '''

    for cruise in sorted_cruises:
        room_type_columns = ''.join(
            [f'<td>{cruise[header].replace("€", "").replace(",", "")}</td>' for header in headers])
        destinations = '<br>'.join(cruise["cruise_destinations"])
        html_content += f'''
        <tr>
            <td>{cruise["cruise_ship"]}</td>
            <td>{cruise["cruise_duration"]}</td>
            <td>{destinations}</td>
            {room_type_columns}
            <td><a href="{cruise["URL"]}" target="_blank">Link</a></td>
        </tr>
        '''

    html_content += '''
            </tbody>
        </table>
    </body>
    </html>
    '''

    with open("resources/results.html", "w") as file:
        file.write(html_content)
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"html/result_{current_date}.html"
    with open(file_name, "w") as file:
        file.write(html_content)
    return html_content
