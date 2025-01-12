from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import statistics
from collections import defaultdict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import io
from flask import Response
import pandas as pd
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.after_request
def after_request(response):
    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def load_data(file_type):
    if file_type == "posts":
        with open('.\Results\posts_with_sentiments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    elif file_type == "comments":
        with open('.\Results\comments_with_sentiments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Group data by filters (subreddit, user)
def group_data(data, filters):
    """Group data by the specified filters."""
    field_mapping = {
        "subreddit": "subreddit",
        "user": "author"
    }

    grouped = defaultdict(list)
    for item in data:
        key = item.get(field_mapping.get(filters[0], "unknown"), "unknown")
        grouped[key].append(item)
    return grouped

# Filter data based on timeframes
def filter_by_time(data, timeframe, value):
    result = []
    for item in data:
        created_date = datetime.utcfromtimestamp(item["created_utc"])
        if timeframe == "seasons":
            season = (created_date.month % 12 + 3) // 3  # Map months to seasons
            if season == value:
                result.append(item)
        elif timeframe == "months" and created_date.month == value:
            result.append(item)
        elif timeframe == "years" and created_date.year == value:
            result.append(item)
    return result

# Perform a single query analysis
def analyze_single_query(data, sentiments, metrics, timeframe=None, timeframe_value=None,measures=[], filters=[]):
    filtered_data = data

    # Apply timeframe filter
    if timeframe:
        filtered_data = filter_by_time(data, timeframe, timeframe_value)
    

    

    # return analysis

    # Prepare the analysis results
    analysis = {}
    total_count = len(filtered_data)

    if filters:
        primary_filter = filters[0]  # The top-level grouping
        secondary_filter = filters[1] if len(filters) > 1 else None  # Nested grouping (if any)

        # Perform top-level grouping
        grouped_data = group_data(filtered_data, [primary_filter])

        for primary_key, primary_items in grouped_data.items():
            primary_analysis = {}

            # Perform nested grouping if a secondary filter is specified
            if secondary_filter:
                nested_grouped_data = group_data(primary_items, [secondary_filter])
                for secondary_key, secondary_items in nested_grouped_data.items():
                    # Calculate metrics for the secondary group
                    primary_analysis[secondary_key] = calculate_metrics(secondary_items, sentiments, metrics, measures)
            else:
                # Calculate metrics directly if no secondary grouping
                primary_analysis = calculate_metrics(primary_items, sentiments, metrics, measures)

            # Assign to the top-level key
            analysis[primary_key] = primary_analysis
    else:
        # No grouping; calculate metrics for the entire dataset
        analysis = calculate_metrics(filtered_data, sentiments, metrics, measures)
    
    return analysis
    # Count sentiments if "nombre" is in metrics
    if "nombre" in metrics:
        for sentiment in sentiments:
            if sentiment == "positifs":
                analysis["nombre_positifs"] = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "positive")
            elif sentiment == "negatifs":
                analysis["nombre_negatifs"] = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "negative")
            elif sentiment == "neutres":
                analysis["nombre_neutres"] = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "neutral")
    if "pourcentage" in metrics:
        for sentiment in sentiments:
            if sentiment == "positifs":
                analysis["pourcentage_positifs"] = str(round((sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "positive")/total_count)*100,2))+' %'
            elif sentiment == "negatifs":
                analysis["pourcentage_negatifs"] = str(round((sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "negative")/total_count)*100,2))+' %'
            elif sentiment == "neutres":
                analysis["pourcentage_neutres"] = str(round((sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "neutral")/total_count)*100,2)) +' %'


    if any(measure in measures for measure in ["moyenne", "médiane", "maximal", "minimal"]):
        compound_scores = [item['content_sentiment']['compound'] for item in filtered_data]

        if compound_scores:  # Ensure there are scores to calculate
            if "moyenne" in measures:
                analysis["moyenne"] = round(statistics.mean(compound_scores), 4)
            if "médiane" in measures:
                analysis["médiane"] = round(statistics.median(compound_scores), 4)
            if "maximal" in measures:
                analysis["maximal"] = round(max(compound_scores), 4)
            if "minimal" in measures:
                analysis["minimal"] = round(min(compound_scores), 4)

    return analysis


def calculate_metrics(filtered_data, sentiments, metrics, measures):
    """Calculate counts, percentages, and measures for a given group or dataset."""
    analysis = {}
    total_count = len(filtered_data)

    if total_count == 0:
        return {"error": "No data available."}

    # Count sentiments and calculate percentages
    # if "nombre" in metrics:
    #     for sentiment in sentiments:
    #         if sentiment == "positifs":
    #             analysis["nombre_positifs"] = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "positive")
    #         elif sentiment == "negatifs":
    #             analysis["nombre_negatifs"] = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "negative")
    #         elif sentiment == "neutres":
    #             analysis["nombre_neutres"] = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "neutral")
    # if "pourcentage" in metrics:
    #     for sentiment in sentiments:
    #         if sentiment == "positifs":
    #             analysis["pourcentage_positifs"] = str(round((sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "positive")/total_count)*100,2))+' %'
    #         elif sentiment == "negatifs":
    #             analysis["pourcentage_negatifs"] = str(round((sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "negative")/total_count)*100,2))+' %'
    #         elif sentiment == "neutres":
    #             analysis["pourcentage_neutres"] = str(round((sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "neutral")/total_count)*100,2)) +' %'


    if "nombre" in metrics:
        for sentiment in sentiments:
            if sentiment == "positifs":
                positive_types = ["positive", "relatively positive", "very positive", "extremely positive"]
                sentiment_counts = {ptype: sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == ptype) for ptype in positive_types}
                total_positives = sum(sentiment_counts.values())

                # Add counts for each type under "positifs"
                analysis["positifs"] = {ptype.replace(' ', '_'): count for ptype, count in sentiment_counts.items()}
                # Add total count for "positifs"
                analysis["positifs"]["total"] = total_positives

            elif sentiment == "negatifs":
                negative_types = ["negative", "relatively negative", "very negative", "extremely negative"]
                sentiment_counts = {ntype: sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == ntype) for ntype in negative_types}
                total_negatives = sum(sentiment_counts.values())

                # Add counts for each type under "negatifs"
                analysis["negatifs"] = {ntype.replace(' ', '_'): count for ntype, count in sentiment_counts.items()}
                # Add total count for "negatifs"
                analysis["negatifs"]["total"] = total_negatives

            elif sentiment == "neutres":
                neutral_count = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "neutral")
                analysis["neutres"] = {"total": neutral_count}

    # Calculate sentiment percentages ("pourcentage")
    if "pourcentage" in metrics:
        for sentiment in sentiments:
            if sentiment == "positifs":
                positive_types = ["positive", "relatively positive", "very positive", "extremely positive"]
                sentiment_counts = {ptype: sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == ptype) for ptype in positive_types}
                total_positives = sum(sentiment_counts.values())

                # Add percentages for each type under "positifs"
                analysis["positifs"] = analysis.get("positifs", {})
                for ptype, count in sentiment_counts.items():
                    analysis["positifs"][f"{ptype.replace(' ', '_')}_pourcentage"] = f"{round((count / total_count) * 100, 2)} %"
                # Add total percentage for "positifs"
                analysis["positifs"]["total_pourcentage"] = f"{round((total_positives / total_count) * 100, 2)} %"

            elif sentiment == "negatifs":
                negative_types = ["negative", "relatively negative", "very negative", "extremely negative"]
                sentiment_counts = {ntype: sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == ntype) for ntype in negative_types}
                total_negatives = sum(sentiment_counts.values())

                # Add percentages for each type under "negatifs"
                analysis["negatifs"] = analysis.get("negatifs", {})
                for ntype, count in sentiment_counts.items():
                    analysis["negatifs"][f"{ntype.replace(' ', '_')}_pourcentage"] = f"{round((count / total_count) * 100, 2)} %"
                # Add total percentage for "negatifs"
                analysis["negatifs"]["total_pourcentage"] = f"{round((total_negatives / total_count) * 100, 2)} %"

            elif sentiment == "neutres":
                neutral_count = sum(1 for item in filtered_data if item['content_sentiment']['sentiment'] == "neutral")
                neutral_percentage = f"{round((neutral_count / total_count) * 100, 2)} %"
                analysis["neutres"] = analysis.get("neutres", {})
                analysis["neutres"]["total_pourcentage"] = neutral_percentage


    if any(measure in measures for measure in ["moyenne", "médiane", "maximal", "minimal"]):
        compound_scores = [item['content_sentiment']['compound'] for item in filtered_data]

        if compound_scores:  # Ensure there are scores to calculate
            if "moyenne" in measures:
                analysis["moyenne"] = round(statistics.mean(compound_scores), 4)
            if "médiane" in measures:
                analysis["médiane"] = round(statistics.median(compound_scores), 4)
            if "maximal" in measures:
                analysis["maximal"] = round(max(compound_scores), 4)
            if "minimal" in measures:
                analysis["minimal"] = round(min(compound_scores), 4)

    return analysis


@app.route('/command', methods=['POST'])
def handle_command():
    # Parse the JSON payload
    payload = request.get_json()
    instructions = payload.get("instructions", {})
    if not instructions:
        return jsonify({"error": "No instructions provided"}), 400

    # Extract instruction components
    files = instructions.get("files", [])
    sentiments = instructions.get("sentiments", [])
    metrics = instructions.get("metrics", [])
    measures = instructions.get("measures", [])
    timeframes = instructions.get("timeframes", [])
    filters = instructions.get("filters", [])

    # Define results container
    results = {}

    # Season names in French
    season_names = {1: "printemps", 2: "été", 3: "automne", 4: "hiver"}
    month_names = {1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: 'mai', 6: 'juin', 7: 'juillet', 8: 'août', 9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'}

    # Process each file type
    for file_type in files:
        data = load_data(file_type)
        file_results = {}

        if not timeframes:  # If no timeframes are specified
            season_results = analyze_single_query(
                data=data,
                sentiments=sentiments,
                metrics=metrics,
                timeframe=None,  # No timeframe filtering
                timeframe_value=None,  # No specific timeframe value
                measures=measures,
                filters=filters
            )
            file_results['results'] = season_results
        else:
            # Use nested loops to process the specified timeframes
            # for i, outer_timeframe in enumerate(timeframes):
            #     outer_values = {datetime.utcfromtimestamp(item["created_utc"]).year for item in data} if outer_timeframe == "années" else \
            #                    [1, 2, 3, 4] if outer_timeframe == "saisons" else list(range(1, 13))

            #     for outer_value in outer_values:
            #         outer_filtered_data = [
            #             item for item in data if
            #             (outer_timeframe == "années" and datetime.utcfromtimestamp(item["created_utc"]).year == outer_value) or
            #             (outer_timeframe == "saisons" and (datetime.utcfromtimestamp(item["created_utc"]).month % 12 + 3) // 3 == outer_value) or
            #             (outer_timeframe == "mois" and datetime.utcfromtimestamp(item["created_utc"]).month == outer_value)
            #         ]
            #         outer_key = f"année_{outer_value}" if outer_timeframe == "années" else \
            #                     season_names.get(outer_value, f"saison_{outer_value}") if outer_timeframe == "saisons" else \
            #                     month_names.get(outer_value, f"mois_{outer_value}")

            #         if outer_key not in file_results:
            #             file_results[outer_key] = {}

            #         for j, inner_timeframe in enumerate(timeframes[i + 1:]):
            #             inner_values = {datetime.utcfromtimestamp(item["created_utc"]).year for item in outer_filtered_data} if inner_timeframe == "années" else \
            #                            [1, 2, 3, 4] if inner_timeframe == "saisons" else list(range(1, 13))

            #             for inner_value in inner_values:
            #                 inner_filtered_data = [
            #                     item for item in outer_filtered_data if
            #                     (inner_timeframe == "années" and datetime.utcfromtimestamp(item["created_utc"]).year == inner_value) or
            #                     (inner_timeframe == "saisons" and (datetime.utcfromtimestamp(item["created_utc"]).month % 12 + 3) // 3 == inner_value) or
            #                     (inner_timeframe == "mois" and datetime.utcfromtimestamp(item["created_utc"]).month == inner_value)
            #                 ]
            #                 inner_key = f"année_{inner_value}" if inner_timeframe == "années" else \
            #                             season_names.get(inner_value, f"saison_{inner_value}") if inner_timeframe == "saisons" else \
            #                             month_names.get(inner_value, f"mois_{inner_value}")

            #                 analysis_results = analyze_single_query(
            #                     inner_filtered_data,
            #                     sentiments,
            #                     metrics,
            #                     timeframe=None,  # No more filtering beyond this point
            #                     timeframe_value=None,
            #                     measures=measures,
            #                     filters=filters,
            #                 )

            #                 if inner_key not in file_results[outer_key]:
            #                     file_results[outer_key][inner_key] = analysis_results
            #                 else:
            #                     file_results[outer_key][inner_key].update(analysis_results)
            file_results = group_data_by_timeframes(
                data=data,
                timeframes=timeframes,
                index=0,
                sentiments=sentiments,
                metrics=metrics,
                measures=measures,
                filters=filters,
                season_names=season_names,
                month_names=month_names
            )
            results[file_type] = file_results

        results[file_type] = file_results

    return jsonify({"status": "success", "results": results}), 200
    
def group_data_by_timeframes(data, timeframes, index, sentiments, metrics, measures, filters, season_names, month_names):
    """
    Recursively group the data by each timeframe in timeframes.
    Once we reach the last timeframe, we call analyze_single_query on that subset.
    
    :param data: The current subset of data to analyze
    :param timeframes: The full list of requested timeframes, e.g. ["années", "saisons", "mois"]
    :param index: The current index in the timeframes list
    :param sentiments: List of sentiments to measure
    :param metrics: List of metrics to compute (nombre, pourcentage, etc.)
    :param measures: List of numeric measures (moyenne, médiane, etc.)
    :param filters: Additional grouping filters, e.g. ["subreddit"] or ["user"]
    :param season_names: Dictionary mapping season number 1..4 to a name
    :param month_names: Dictionary mapping month 1..12 to a name
    :return: A nested dictionary of results
    """
    # If we've used up all timeframes, just analyze this subset with no further time-grouping
    if index >= len(timeframes):
        return analyze_single_query(
            data=data,
            sentiments=sentiments,
            metrics=metrics,
            timeframe=None,
            timeframe_value=None,
            measures=measures,
            filters=filters
        )
    
    current_timeframe = timeframes[index]
    
    # Determine the unique values for this timeframe
    if current_timeframe == 'années':
        unique_values = sorted({datetime.utcfromtimestamp(item["created_utc"]).year for item in data})
    elif current_timeframe == 'saisons':
        # 1 = printemps, 2 = été, 3 = automne, 4 = hiver
        unique_values = [1, 2, 3, 4]
    elif current_timeframe == 'mois':
        # 1..12
        unique_values = list(range(1, 13))
    else:
        # If an unknown timeframe is passed, just return an error or no grouping
        return {"error": f"Unknown timeframe {current_timeframe}"}
    
    results = {}
    
    # Group data by each unique value of this timeframe
    for val in unique_values:
        # Filter the data subset for this timeframe value
        subset = []
        for item in data:
            dt = datetime.utcfromtimestamp(item["created_utc"])
            
            if current_timeframe == 'années':
                if dt.year == val:
                    subset.append(item)
            elif current_timeframe == 'saisons':
                season = (dt.month % 12 + 3) // 3
                if season == val:
                    subset.append(item)
            elif current_timeframe == 'mois':
                if dt.month == val:
                    subset.append(item)
        
        if not subset:
            # If there's no data at all for this timeframe value, we can skip or store an empty result
            # For clarity, you can decide if you prefer an empty dict or just skip it.
            continue
        
        # Build the dictionary key
        if current_timeframe == 'années':
            key = f"année_{val}"
        elif current_timeframe == 'saisons':
            key = season_names.get(val, f"saison_{val}")
        else:  # 'mois'
            key = month_names.get(val, f"mois_{val}")
        
        # Recursively group or analyze further
        results[key] = group_data_by_timeframes(
            data=subset,
            timeframes=timeframes,
            index=index + 1, 
            sentiments=sentiments,
            metrics=metrics,
            measures=measures,
            filters=filters,
            season_names=season_names,
            month_names=month_names
        )
    
    return results

analyzer = SentimentIntensityAnalyzer()

def classify_sentiment(compound):
    if compound >= 0.9:
        return "extremely positive"
    elif compound >= 0.7:
        return "very positive"
    elif compound >= 0.5:
        return "positive"
    elif compound > 0.2:
        return "relatively positive"
    elif compound >= -0.2:
        return "neutral"
    elif compound > -0.5:
        return "relatively negative"
    elif compound > -0.7:
        return "negative"
    elif compound > -0.9:
        return "very negative"
    else:
        return "extremely negative"

@app.route('/chat', methods=['POST'])
def analyze_sentiment():
    data = request.json
    sentence = data.get('sentence', '')  # Récupérer la phrase du corps de la requête
    machineLearning = data.get('machineLearning', '')  # Récupérer la phrase du corps de la requête
    if not sentence:
        return jsonify({"error": "No sentence provided"}), 400
    if machineLearning == True:
        return jsonify({"error": "NoT yet integrated"}), 400
    else:
        sentiment_scores = analyzer.polarity_scores(sentence)
        sentiment = classify_sentiment(sentiment_scores['compound'])
        # Ajouter le sentiment à la réponse
        sentiment_scores['sentiment'] = sentiment
        return jsonify(sentiment_scores)

# @app.route('/chat', methods=['POST'])
# def handle_chat():
#     try:
#         # Parse JSON from the request body
#         data = request.get_json()
#         print(str(data))
#         if not data:
#             return jsonify({"error": "No JSON provided"}), 400

#         # Process the chat message
        

#         # Simulate a response
#         response = {
#             "status": "success",
#             "reply": f"Received your message: {str(data)}",
#             "ai_enabled": data.get('machine_learning', False)
#         }
#         return jsonify(data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500





@app.route('/export', methods=['POST'])
def handle_export():
    # Parse the JSON payload
    payload = request.get_json()
    instructions = payload.get("instructions", {})
    if not instructions:
        return jsonify({"error": "No instructions provided"}), 400

    # Extract instruction components
    files = instructions.get("files", [])
    sentiments = instructions.get("sentiments", [])
    timeframes = instructions.get("timeframes", [])
    filters = instructions.get("filters", [])
    export = instructions.get("export", False)  # Check for export flag

    # Names for seasons and months
    season_names = {1: "printemps", 2: "été", 3: "automne", 4: "hiver"}
    month_names = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: 'mai', 6: 'juin', 7: 'juillet', 8: 'août',
        9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'
    }

    # Filtered data container
    filtered_data = []

    # Process each file type
    for file_type in files:
        data = load_data(file_type)

        # Filter data based on the given criteria
        if not timeframes:  # No specific timeframes
            filtered_data.extend(apply_filters(data, sentiments, filters))
        else:
            for timeframe in timeframes:
                if timeframe == "saisons":
                    for season in range(1, 5):  # 1 = Spring, ..., 4 = Winter
                        filtered_season = filter_by_time(data, "seasons", season)
                        for item in filtered_season:
                            item['season'] = season_names[season]
                        filtered_data.extend(filtered_season)
                elif timeframe == "mois":
                    for month in range(1, 13):  # 1 = January, ..., 12 = December
                        filtered_month = filter_by_time(data, "months", month)
                        for item in filtered_month:
                            item['month'] = month_names[month]
                        filtered_data.extend(filtered_month)
                elif timeframe == "années":
                    unique_years = {datetime.utcfromtimestamp(item["created_utc"]).year for item in data}
                    for year in unique_years:
                        filtered_year = filter_by_time(data, "years", year)
                        for item in filtered_year:
                            item['year'] = year
                        filtered_data.extend(filtered_year)

    # If export is enabled, generate a CSV file with the filtered data
    if export:
        return create_excel_response(filtered_data)

    # Default response if export is not requested
    return jsonify({"status": "success", "filtered_data": filtered_data}), 200


def apply_filters(data, sentiments, filters):
    """Filter data by sentiments and additional filter criteria."""
    return [
        item for item in data
        if item['content_sentiment']['sentiment'] in sentiments
        and all(filter_key in item and item[filter_key] == filter_value for filter_key, filter_value in filters)
    ]


def filter_by_timeframe(data, sentiments, filters, timeframe, value):
    """Filter data by specific timeframes."""
    filtered_data = select_by_time(data, timeframe, value)
    return apply_filters(filtered_data, sentiments, filters)


def select_by_time(data, timeframe, value):
    """Filter data based on time criteria (e.g., seasons, months, years)."""
    result = []
    for item in data:
        created_date = datetime.utcfromtimestamp(item["created_utc"])
        if timeframe == "seasons":
            season = (created_date.month % 12 + 3) // 3  # Map months to seasons
            if season == value:
                result.append(item)
        elif timeframe == "months" and created_date.month == value:
            result.append(item)
        elif timeframe == "years" and created_date.year == value:
            result.append(item)
    return result


def create_csv_response(filtered_data):
    """Create a CSV response from filtered data."""
    if not filtered_data:
        return jsonify({"error": "No data available to export"}), 400

    # Create an in-memory CSV file
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # Write the header based on keys of the first dictionary
    header = filtered_data[0].keys() if filtered_data else []
    csv_writer.writerow(header)

    # Write the rows
    for row in filtered_data:
        csv_writer.writerow(row.values())

    # Prepare the response
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response

def create_excel_response(filtered_data):
    """Create an Excel response from filtered data."""
    if not filtered_data:
        return jsonify({"error": "No data available to export"}), 400

    # Create a DataFrame from the filtered data
    df = pd.DataFrame(filtered_data)

    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)

    # Prepare the response
    response = Response(
        output.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
