import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from .config import water_colors


def create_carbon_footprint_chart(carbon_kg, carbon_saved_kg):
    total_carbon = carbon_kg + carbon_saved_kg
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=carbon_kg,
        number={'suffix': " kg CO₂", 'font': {'size': 32, 'color': '#FF6B6B'}},
        title={'text': "<b>Carbon Footprint</b>", 'font': {'size': 16, 'color': '#E0E0E0'}},
        gauge={
            'axis': {'range': [0, total_carbon], 'tickformat': ".0f"},
            'bar': {'color': '#FF6B6B'},
            'bgcolor': "#2D2D3A",
            'steps': [
                {'range': [0, total_carbon * 0.5], 'color': '#2D4A2C'},
                {'range': [total_carbon * 0.5, total_carbon], 'color': '#4A2C2C'}
            ]
        }
    ))
    
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)')
    return fig


def create_cumulative_impact_chart(history):
    if not history:
        return None
    
    cumulative_water = []
    cumulative_carbon = []
    items = []
    
    running_water = 0
    running_carbon = 0
    
    for i, analysis in enumerate(history, 1):
        running_water += analysis.total_liters
        running_carbon += getattr(analysis, 'carbon_kg', 0)
        cumulative_water.append(running_water)
        cumulative_carbon.append(running_carbon)
        items.append(f"Item {i}")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=items, y=cumulative_water, name="Water (L)", 
                   line=dict(color='#64B5F6', width=3),
                   fill='tozeroy', fillcolor='rgba(100, 181, 246, 0.2)'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=items, y=cumulative_carbon, name="CO₂ (kg)", 
                   line=dict(color='#FF6B6B', width=3),
                   fill='tozeroy', fillcolor='rgba(255, 107, 107, 0.2)'),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Products Scanned", color='#B0B0B0')
    fig.update_yaxes(title_text="Water (Liters)", secondary_y=False, color='#64B5F6')
    fig.update_yaxes(title_text="CO₂ (kg)", secondary_y=True, color='#FF6B6B')
    
    fig.update_layout(
        title=dict(text="<b>Cumulative Environmental Impact</b>", x=0.5, font=dict(size=18, color='#E0E0E0')),
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
    )
    return fig


def create_regional_context_map(regional_impact):
    if not regional_impact or not regional_impact.high_stress_regions:
        return None
    
    regions = regional_impact.high_stress_regions[:5]
    multipliers = [regional_impact.scarcity_multiplier] * len(regions)
    
    fig = go.Figure(go.Bar(
        y=regions,
        x=multipliers,
        orientation='h',
        marker=dict(color='#FF6B6B', line=dict(color='#C62828', width=2)),
        text=[f"{m:.1f}x impact" for m in multipliers],
        textposition='inside',
        textfont=dict(color='white', size=12)
    ))
    
    fig.update_layout(
        title=dict(text="<b>🌍 Water-Stressed Regions</b>", x=0.5, font=dict(size=16, color='#E0E0E0')),
        xaxis=dict(title="Impact Multiplier", color='#B0B0B0'),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=40)
    )
    return fig


def create_water_gauge(total_liters, max_liters=None, title="Water Footprint"):
    if max_liters is None:
        magnitude = 10 ** int(np.log10(total_liters + 1))
        max_liters = np.ceil(total_liters / magnitude) * magnitude * 1.2
    
    ratio = total_liters / max_liters
    bar_color = "#4CAF50" if ratio < 0.3 else "#FFC107" if ratio < 0.6 else "#F44336"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=total_liters,
        number={'suffix': " L", 'font': {'size': 48, 'color': '#1E88E5', 'family': 'Arial Black'}},
        title={'text': f"<b>{title}</b>", 'font': {'size': 20, 'color': '#E0E0E0'}},
        gauge={
            'axis': {'range': [0, max_liters], 'tickwidth': 2, 'tickcolor': "#9E9E9E", 'tickformat': ",.0f", 'ticksuffix': " L", 'tickfont': {'color': '#B0B0B0'}},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "#2D2D3A",
            'borderwidth': 2,
            'bordercolor': "#3D3D4A",
            'steps': [
                {'range': [0, max_liters * 0.3], 'color': '#1B4332'},
                {'range': [max_liters * 0.3, max_liters * 0.6], 'color': '#3D3D1A'},
                {'range': [max_liters * 0.6, max_liters], 'color': '#4A2C2C'}
            ],
            'threshold': {'line': {'color': "#1E88E5", 'width': 4}, 'thickness': 0.8, 'value': total_liters}
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=30, r=30, t=60, b=30), paper_bgcolor='rgba(0,0,0,0)')
    return fig


def create_water_breakdown_donut(analysis):
    labels = ['Green Water<br>(Rainwater)', 'Blue Water<br>(Surface/Ground)', 'Grey Water<br>(Polluted)']
    values = [analysis.green_water_liters, analysis.blue_water_liters, analysis.grey_water_liters]
    percentages = [analysis.breakdown.green_water_pct, analysis.breakdown.blue_water_pct, analysis.breakdown.grey_water_pct]
    colors = [water_colors.GREEN_WATER, water_colors.BLUE_WATER, water_colors.GREY_WATER]
    
    hover_text = [f"<b>{labels[i]}</b><br>{values[i]:,.0f} L ({percentages[i]:.1f}%)" for i in range(3)]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='#1E1E2E', width=3)),
        textinfo='percent',
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_text,
        pull=[0.02, 0.02, 0.02]
    ))
    
    fig.add_annotation(
        text=f"<b>{analysis.total_liters:,.0f}</b><br>Liters",
        x=0.5, y=0.5,
        font=dict(size=22, color='#1E88E5'),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(text="<b>Water Type Breakdown</b>", x=0.5, font=dict(size=18, color='#E0E0E0')),
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11))
    )
    return fig


def create_comparison_bar_chart(original_name, original_liters, swap_name, swap_liters, savings_pct):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=[f"<b>{original_name}</b>"], x=[original_liters], orientation='h',
        marker=dict(color='#EF5350', line=dict(color='#C62828', width=2)),
        text=f"{original_liters:,.0f} L", textposition='auto',
        textfont=dict(color='white', size=14, family='Arial Black')
    ))
    
    fig.add_trace(go.Bar(
        y=[f"<b>{swap_name}</b>"], x=[swap_liters], orientation='h',
        marker=dict(color='#66BB6A', line=dict(color='#2E7D32', width=2)),
        text=f"{swap_liters:,.0f} L", textposition='auto',
        textfont=dict(color='white', size=14, family='Arial Black')
    ))
    
    fig.add_annotation(
        x=original_liters * 0.5, y=0.5,
        text=f"<b>💧 Save {savings_pct:.0f}%</b>",
        showarrow=False, font=dict(size=16, color='#64B5F6'),
        bgcolor='rgba(30, 60, 90, 0.9)', borderpad=8, bordercolor='#64B5F6', borderwidth=2
    )
    
    fig.update_layout(
        title=dict(text="<b>🔄 Sustainable Swap</b>", x=0.5, font=dict(size=18, color='#E0E0E0')),
        xaxis=dict(title="Water Footprint (Liters)", tickformat=",.0f", gridcolor='#3D3D4A', tickfont=dict(color='#B0B0B0')),
        height=250, margin=dict(l=20, r=20, t=60, b=50),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, bargap=0.4
    )
    return fig


def create_impact_comparison_cards(metrics):
    comparisons = [
        ("🚿", "Showers", metrics.shower_minutes_equivalent / 10, "10-min showers"),
        ("🚽", "Flushes", metrics.toilet_flushes_equivalent, "toilet flushes"),
        ("🍽️", "Dishes", metrics.dishwasher_cycles_equivalent, "dishwasher loads"),
        ("👕", "Laundry", metrics.washing_machine_cycles_equivalent, "wash cycles"),
    ]
    
    fig = make_subplots(
        rows=1, cols=4,
        subplot_titles=[f"{c[0]} {c[1]}" for c in comparisons],
        specs=[[{"type": "indicator"}] * 4]
    )
    
    for i, (_, _, value, unit) in enumerate(comparisons, 1):
        fig.add_trace(
            go.Indicator(
                mode="number", value=value,
                number={'font': {'size': 36, 'color': '#1E88E5'}, 'valueformat': ',.0f'},
                title={'text': f"<span style='font-size:12px;color:#B0B0B0'>{unit}</span>"}
            ),
            row=1, col=i
        )
    
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig


def create_water_drop_animation():
    return """
    <style>
    @keyframes water-drop {
        0% { transform: translateY(-10px); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateY(10px); opacity: 0; }
    }
    .water-drop { display: inline-block; animation: water-drop 1.5s ease-in-out infinite; }
    .water-drop:nth-child(2) { animation-delay: 0.3s; }
    .water-drop:nth-child(3) { animation-delay: 0.6s; }
    .water-container { display: flex; justify-content: center; gap: 10px; font-size: 2rem; }
    </style>
    <div class="water-container">
        <span class="water-drop">💧</span>
        <span class="water-drop">💧</span>
        <span class="water-drop">💧</span>
    </div>
    """


def create_confidence_indicator(confidence):
    if confidence >= 0.8:
        color, label = "#4CAF50", "High"
    elif confidence >= 0.5:
        color, label = "#FFC107", "Medium"
    else:
        color, label = "#F44336", "Low"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        number={'suffix': "%", 'font': {'size': 24, 'color': color}},
        title={'text': f"Confidence: {label}", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'visible': False},
            'bar': {'color': color, 'thickness': 1},
            'bgcolor': "#2D2D3A", 'borderwidth': 0,
        }
    ))
    
    fig.update_layout(height=120, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig
