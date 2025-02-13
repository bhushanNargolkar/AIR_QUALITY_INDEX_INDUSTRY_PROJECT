from flask import Flask, render_template, request
import json
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta

app = Flask(__name__)

# Load the AQI data
with open('aqi_index_dataset.json', 'r') as f:
    aqi_data = json.load(f)

@app.route('/')
def index():
    # Get list of cities
    cities = list(aqi_data.keys())
    # Get list of pollutants
    pollutants = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
    return render_template('index.html', cities=cities, pollutants=pollutants)

@app.route('/plot', methods=['POST'])
def plot():
    city = request.form['city']
    pollutant = request.form['pollutant']
    time_range = request.form['time_range']
    viz_type = request.form['viz_type']

    if city in aqi_data and 'data' in aqi_data[city]:
        city_data = aqi_data[city]['data']
        if 'forecast' in city_data and 'daily' in city_data['forecast']:
            forecast_data = city_data['forecast']['daily']
            
            if pollutant in forecast_data:
                data = forecast_data[pollutant]
                
                # Filter data based on time range
                today = datetime.now()
                if time_range == '1day':
                    start_date = today - timedelta(days=1)
                elif time_range == '1week':
                    start_date = today - timedelta(days=7)
                else:  # '1month'
                    start_date = today - timedelta(days=30)
                
                filtered_data = [d for d in data if datetime.strptime(d['day'], '%Y-%m-%d') >= start_date]
                
                # Create different types of visualizations
                if viz_type == 'line':
                    trace = go.Scatter(
                        x=[d['day'] for d in filtered_data],
                        y=[d['avg'] for d in filtered_data],
                        mode='lines+markers',
                        name=f'{pollutant.upper()} levels'
                    )
                elif viz_type == 'bar':
                    trace = go.Bar(
                        x=[d['day'] for d in filtered_data],
                        y=[d['avg'] for d in filtered_data],
                        name=f'{pollutant.upper()} levels'
                    )
                else:  # heatmap
                    trace = go.Heatmap(
                        z=[[d['avg']] for d in filtered_data],
                        x=[d['day'] for d in filtered_data],
                        y=[pollutant.upper()],
                        colorscale='Viridis'
                    )
                
                layout = go.Layout(
                    title=f'{pollutant.upper()} Levels in {city.capitalize()}',
                    xaxis={'title': 'Date'},
                    yaxis={'title': f'{pollutant.upper()} Level'},
                    template='plotly_dark'
                )
                
                fig = go.Figure(data=[trace], layout=layout)
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                
                return render_template('plot.html', graphJSON=graphJSON)

    return "No data available for the selected criteria"

if __name__ == '__main__':
    app.run(debug=True)