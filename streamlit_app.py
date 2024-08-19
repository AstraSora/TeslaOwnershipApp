import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def calculate_annualized_maintenance(maintenance_items):
    annualized_costs = {}
    for item, details in maintenance_items.items():
        if "interval_years" in details:
            annualized_costs[item] = details["cost"] / details["interval_years"]
        elif "interval_miles" in details:
            annual_miles = details["miles_per_year"]
            annualized_costs[item] = (details["cost"] * annual_miles) / details["interval_miles"]
    return annualized_costs

# Default values
monthly_payment = 469  # Monthly car payment in USD
insurance_per_month = 323.56  # Monthly insurance cost in USD
miles_per_year = 12500  # Annual mileage
initial_value = 45000  # Initial purchase price of the car in USD
depreciation_rate = 0.10  # Annual depreciation rate (10%)
cost_per_kwh = 0.13  # Cost per kWh in USD (default value)
miles_per_kwh = 3.26  # Efficiency of Tesla Model 3 (miles per kWh)
night_cost_per_kwh = 0.10  # Cost per kWh during the night in USD
day_cost_per_kwh = 0.15  # Cost per kWh during the day in USD

maintenance_items = {
    "Cabin Air Filter Replacement": {"cost": 70, "interval_years": 2},
    "AC Desiccant Bag Replacement": {"cost": 250, "interval_years": 5},
    "Brake Caliper Cleaning and Lubrication": {"cost": 125, "interval_miles": 12500, "miles_per_year": miles_per_year},
    "Brake Fluid Check/Replacement": {"cost": 125, "interval_years": 3},
    "Tire Rotation": {"cost": 40, "interval_miles": 6250, "miles_per_year": miles_per_year},
    "Tire Replacement": {"cost": 1200, "interval_miles": 25000, "miles_per_year": miles_per_year}
}

monthly_detailing_cost = 50  # Monthly car detailing/washes in USD
one_time_fees = {
    "COOLCRAZY Dash Cam 4K": 69.99,
    "LANTU Model 3 Rear Screen Protector": 12.99,
    "psler Jack Pad": 12.99,
    "Wigoo 2024 Tesla Model 3 Mud Flaps": 29.99,
    "KUNIST 2024 Model 3 Console Organizer": 20.79,
    "SUMK Tempered Glass Screen Protector": 25.49,
    "Tesla Model 3 Highland Floor Mats": 132.29,
    "Tesla Universal Wall Connector": 580.00
}

# User inputs
st.title("Tesla Model 3 Cost of Ownership")
st.text("This models cash accounting, so depreciation is shown separately at the very end.")

# Display Image of Tesla
st.image("M3.webp", caption="2024 Tesla Model 3 LR RWD Refresh", use_column_width=True)

monthly_payment = st.number_input("Monthly Car Payment (USD)", value=monthly_payment)
insurance_per_month = st.number_input("Monthly Insurance Cost (USD)", value=insurance_per_month)
monthly_detailing_cost = st.number_input("Monthly Car Detailing Cost (USD)", value=monthly_detailing_cost)
miles_per_year = st.number_input("Miles Driven Per Year", value=miles_per_year)
cost_per_kwh = st.number_input("Cost per kWh (USD)", value=cost_per_kwh)

# Calculate electricity cost
annual_electricity_cost = (miles_per_year / miles_per_kwh) * cost_per_kwh
monthly_electricity_cost = annual_electricity_cost / 12

# Create an editable DataFrame for accessories
accessory_df = pd.DataFrame(list(one_time_fees.items()), columns=["Accessory", "Cost (USD)"])
st.subheader("Car Accessories")
edited_accessory_df = st.data_editor(accessory_df, num_rows="dynamic")

# Update the accessory costs based on user edits
accessory_costs = edited_accessory_df.set_index("Accessory")["Cost (USD)"].to_dict()

# Calculate total cost of accessories
total_accessories = sum(accessory_costs.values())

# Display total cost of accessories
st.text(f"Total Cost of Accessories: ${total_accessories:,.2f}")

# Calculations
annualized_maintenance_costs = calculate_annualized_maintenance(maintenance_items)
total_annual_maintenance_costs = sum(annualized_maintenance_costs.values())
annual_car_payment = monthly_payment * 12
annual_insurance = insurance_per_month * 12
annual_detailing_cost = monthly_detailing_cost * 12

total_annual_cost = (annual_car_payment + annual_insurance + total_annual_maintenance_costs +
                     annual_detailing_cost + total_accessories + annual_electricity_cost)
total_monthly_cost = total_annual_cost / 12

# Data for pie charts
annual_cost_data = {
    "Annual Car Payment": annual_car_payment,
    "Annual Insurance": annual_insurance,
    "Annualized Maintenance Costs": total_annual_maintenance_costs,
    "Annual Car Detailing": annual_detailing_cost,
    "Accessories": total_accessories,
    "Electricity Cost": annual_electricity_cost
}

monthly_cost_data = {key: value/12 for key, value in annual_cost_data.items()}

def plot_pie_chart(data, title):
    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_traces(
        hovertemplate='%{label}: $%{value:,.2f}<extra></extra>',
        textinfo='label+percent',
        texttemplate='$%{value:,.2f}<br>(%{percent})'
    )
    fig.update_layout(title_text=title)
    return fig

# Maintenance costs over time for stacked bar chart
maintenance_costs_over_time = pd.DataFrame({
    "Year": range(1, 6),
    "Cabin Air Filter Replacement": [70 if year % 2 == 0 else 0 for year in range(1, 6)],
    "AC Desiccant Bag Replacement": [250 if year % 5 == 0 else 0 for year in range(1, 6)],
    "Brake Caliper Cleaning and Lubrication": [125 for _ in range(1, 6)],
    "Brake Fluid Check/Replacement": [125 if year % 3 == 0 else 0 for year in range(1, 6)],
    "Tire Rotation": [40 * 2 for _ in range(1, 6)],  # Rotations per year
    "Tire Replacement": [1200 if year % 2 == 0 else 0 for year in range(1, 6)]
})

# Stacked Bar Chart
def plot_stacked_bar(data):
    fig = go.Figure()
    for column in data.columns[1:]:
        fig.add_trace(go.Bar(x=data["Year"], y=data[column], name=column))
    fig.update_layout(
        barmode='stack',
        title="Annual Maintenance Costs",
        xaxis_title="Year",
        yaxis_title="Cost (USD)",
        yaxis_tickprefix='$',
        yaxis_tickformat=','
    )
    return fig

# Display Stacked Bar Chart
st.header("Maintenance Cost Breakdown")
st.subheader("Stacked Bar Chart")
st.plotly_chart(plot_stacked_bar(maintenance_costs_over_time))

# Add section discussing miles per kWh and electricity costs
st.subheader("Miles per kWh and Cost of Charging")

# Variables
miles_per_kwh = 3.26  # Tesla Model 3 efficiency (miles per kWh)
night_cost_per_kwh = 0.10  # Cost per kWh during the night in USD
day_cost_per_kwh = 0.15  # Cost per kWh during the day in USD
miles_per_gallon = 25  # ICE vehicle efficiency (miles per gallon)
gas_cost_per_gallon = 4.0  # Cost of gas in USD

# Monthly mileage based on 12,500 miles per year
monthly_mileage = 12500 / 12

# Calculate Tesla Model 3 costs
tesla_night_cost_per_mile = night_cost_per_kwh / miles_per_kwh
tesla_day_cost_per_mile = day_cost_per_kwh / miles_per_kwh
tesla_night_cost_per_month = tesla_night_cost_per_mile * monthly_mileage
tesla_day_cost_per_month = tesla_day_cost_per_mile * monthly_mileage

# Calculate ICE vehicle costs
ice_cost_per_mile = gas_cost_per_gallon / miles_per_gallon
ice_cost_per_month = ice_cost_per_mile * monthly_mileage

# Calculate savings
night_savings_per_month = ice_cost_per_month - tesla_night_cost_per_month
day_savings_per_month = ice_cost_per_month - tesla_day_cost_per_month

# Dynamic markdown using f-strings
st.markdown(f"""
- The Tesla Model 3 has an efficiency of **{miles_per_kwh} miles per kWh**. This means for every kilowatt-hour of electricity, you can drive approximately {miles_per_kwh} miles.
- Charging costs can vary depending on when you charge:
  - **Night Charging**: Cost per kWh is lower at around **\${night_cost_per_kwh}**. This is typically during off-peak hours when electricity demand is lower.
  - **Day Charging**: Cost per kWh is higher at around **\${day_cost_per_kwh}**. This is typically during peak hours when electricity demand is higher.
  
***Comparison with ICE Vehicles:***

- A typical internal combustion engine (ICE) vehicle might average around **{miles_per_gallon} miles per gallon (MPG)**.
- If gas costs **\${gas_cost_per_gallon} per gallon**, the cost per mile would be **\${ice_cost_per_mile:.2f} per mile**.
- In contrast, the Tesla Model 3's cost per mile, based on the provided electricity costs, is:
  - **Night Charging**: \${night_cost_per_kwh} per kWh / {miles_per_kwh} miles per kWh = **\${tesla_night_cost_per_mile:.3f} per mile**.
  - **Day Charging**: \${day_cost_per_kwh} per kWh / {miles_per_kwh} miles per kWh = **\${tesla_day_cost_per_mile:.3f} per mile**.

The Tesla Model 3 costs significantly less per month compared to a typical ICE vehicle, assuming you drive 12,500 miles per year (about {monthly_mileage:.2f} miles per month):

- **Tesla Model 3 Night Charging**: **\${tesla_night_cost_per_month:.2f} per month**
- **Tesla Model 3 Day Charging**: **\${tesla_day_cost_per_month:.2f} per month**
- **ICE Vehicle**: **\${ice_cost_per_month:.2f} per month**

**Savings**:

- **Night Charging**: The Tesla Model 3 costs **\${night_savings_per_month:.2f} less per month** compared to an ICE vehicle.
- **Day Charging**: The Tesla Model 3 costs **\${day_savings_per_month:.2f} less per month** compared to an ICE vehicle.
""")



# Display pie charts
st.header("Monthly Cost Breakdown")
st.subheader(f"Total Monthly Cost: ${total_monthly_cost:,.2f}")
monthly_fig = plot_pie_chart(monthly_cost_data, "Monthly Cost Breakdown")
st.plotly_chart(monthly_fig)

st.header("Annual Cost Breakdown")
st.subheader(f"Total Annual Cost: ${total_annual_cost:,.2f}")
annual_fig = plot_pie_chart(annual_cost_data, "Annual Cost Breakdown")
st.plotly_chart(annual_fig)

# Depreciation Calculation and Graph
years = list(range(0, 6))  # Years from 0 to 5
depreciation_values = [initial_value]  # Start with the initial value at year 0

# Calculate depreciation starting from year 1
for year in range(1, 6):
    depreciation_value = initial_value * (1 - depreciation_rate) ** year
    depreciation_values.append(depreciation_value)

def plot_depreciation_graph(years, values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=values, mode='lines+markers', name='Depreciation'))
    fig.update_layout(
        title="Depreciation of Tesla Model 3 Over Time",
        xaxis_title="Year",
        yaxis_title="Value (USD)",
        yaxis_tickprefix='$',
        yaxis_tickformat=','
    )
    return fig

# Plot the depreciation graph
depreciation_fig = plot_depreciation_graph(years, depreciation_values)
st.header(f"Depreciation Graph of {depreciation_rate * 100:.2f}% YoY")
st.plotly_chart(depreciation_fig)