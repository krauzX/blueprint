
import streamlit as st
from PIL import Image
import io
import random

from src.config import config, validate_config
from src.ai_engine import WaterFootprintAnalyzer
from src.models import WaterFootprintAnalysis, WaterImpactMetrics, AnalysisError
from src.visualizations import (
    create_water_gauge, create_water_breakdown_donut, create_comparison_bar_chart,
    create_impact_comparison_cards, create_confidence_indicator, create_water_drop_animation,
    create_carbon_footprint_chart, create_cumulative_impact_chart, create_regional_context_map
)
from src.analytics import TrendAnalyzer, ChallengeEngine
from src.utils import (
    validate_image, resize_image_if_needed, get_image_mime_type,
    get_relatable_comparison, get_disclaimer, get_category_icon,
    get_impact_level, format_number
)

st.set_page_config(
    page_title=f"{config.APP_NAME} | Water Footprint Analyzer",
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown('''
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");
* { font-family: "Inter", sans-serif; }

.main-header {
    background: radial-gradient(circle at top left, #00c6ff 0%, #0072ff 100%);
    padding: 4rem 2rem; 
    border-radius: 24px; 
    margin-bottom: 2.5rem;
    text-align: center; 
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 114, 255, 0.2);
}

.main-header::before {
    content: "";
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: url("https://www.transparenttextures.com/patterns/water-waves.png");
    opacity: 0.1;
    transform: rotate(-5deg);
}

.main-header h1 { 
    font-size: 3.8rem; 
    margin: 0; 
    font-weight: 800; 
    letter-spacing: -2px;
    text-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

.main-header p { 
    font-size: 1.3rem; 
    margin-top: 1rem; 
    opacity: 0.95; 
    font-weight: 500;
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.4;
}

.metric-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    padding: 1.5rem; border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 8px 30px rgba(0,0,0,0.12); }
.metric-card h3 { color: #a0a0a0; margin: 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
.metric-card .value { font-size: 2rem; font-weight: 700; color: #667eea; margin-top: 0.5rem; }

.impact-badge { 
    display: inline-block; padding: 0.5rem 1rem; border-radius: 20px; 
    font-size: 0.85rem; font-weight: 600; letter-spacing: 0.5px;
}
.impact-low { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
.impact-medium { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.impact-high { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }

.swap-card { 
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 2rem; border-radius: 20px; color: white;
    box-shadow: 0 10px 40px rgba(17, 153, 142, 0.3);
}

.product-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    padding: 2rem; border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.section-title {
    font-size: 1.5rem; font-weight: 700; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 2rem 0 1rem 0;
}

[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 12px 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
''', unsafe_allow_html=True)

if 'result' not in st.session_state:
    st.session_state.result = None
if 'image' not in st.session_state:
    st.session_state.image = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'total_water' not in st.session_state:
    st.session_state.total_water = 0
if 'total_carbon' not in st.session_state:
    st.session_state.total_carbon = 0
if 'challenge' not in st.session_state:
    st.session_state.challenge = ChallengeEngine.generate_weekly_challenge([])

st.markdown(
    f'<div class="main-header">'
    f'<h1>{config.APP_ICON} {config.APP_NAME}</h1>'
    f'<p>Unmask the invisible environmental cost of your consumption. Scan any product to reveal its real-world water and carbon impact instantly.</p>'
    f'</div>', 
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown(f'<h2 style="color: #667eea; font-weight: 700; margin-bottom: 1.5rem;">{config.APP_ICON} Your Impact</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("💧 Water", format_number(st.session_state.total_water) + "L", delta=None)
    col2.metric("🌍 Carbon", f"{st.session_state.total_carbon:.0f}kg", delta=None)
    
    if len(st.session_state.history) >= 3:
        analyzer = TrendAnalyzer(st.session_state.history)
        milestone = analyzer.get_milestone_progress(st.session_state.total_water)
        
        if milestone.get('next'):
            st.markdown("---")
            st.markdown(f'<h3 style="color: #667eea; font-size: 1.1rem; font-weight: 600;">🎯 Progress</h3>', unsafe_allow_html=True)
            st.markdown(f"**{milestone['current']}** → {milestone['next']}")
            st.progress(min(milestone['progress_pct'] / 100, 1.0))
            st.caption(f"{milestone['remaining']:,.0f}L to next level")
    
    st.markdown("---")
    st.markdown(f'<h3 style="color: #667eea; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem;">💧 Water Types</h3>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 0.9rem; line-height: 1.8;">🟢 <b>Green</b>: Rainwater<br>🔵 <b>Blue</b>: Surface/ground<br>⚫ <b>Grey</b>: Polluted</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    facts = [
        "A t-shirt needs 2,700L of water.",
        "1kg beef = 15,400L water.",
        "Your phone took 13,000L to make.",
        "Average person uses 4,000L daily."
    ]
    st.caption(random.choice(facts))
    st.caption(f"v{config.APP_VERSION}")

ok, err = validate_config()
if not ok:
    st.error(f"⚠️ {err}")
    st.info("Add your API key to `.streamlit/secrets.toml`:")
    st.code('GEMINI_API_KEY = "your_key_here"', language="toml")
    st.caption("Or set environment variable: `GEMINI_API_KEY=your_key`")
    st.stop()

st.markdown('<div class="section-title">📸 Analyze a Product</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Take Photo"])

image_data = None
with tab1:
    uploaded = st.file_uploader(
        "Drop your product photo here",
        type=['jpg', 'jpeg', 'png', 'webp']
    )
    if uploaded:
        image_data = uploaded.getvalue()
        st.success(f"✓ {uploaded.name} loaded")

with tab2:
    camera = st.camera_input("📷 Snap a photo")
    if camera:
        image_data = camera.getvalue()
        st.success("✓ Got it!")


if image_data:
    valid, err = validate_image(image_data)
    if not valid:
        st.error(f"⚠️ {err}")
        st.stop()
    
    image_data = resize_image_if_needed(image_data)
    st.markdown("---")
    
    col, _ = st.columns([1, 3])
    if col.button("🔍 Analyze", type="primary", use_container_width=True):
        with st.spinner(""):
            st.markdown(create_water_drop_animation(), unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #1E88E5;'><b>Uncovering hidden water...</b></p>", unsafe_allow_html=True)
            
            analyzer = WaterFootprintAnalyzer()
            mime = get_image_mime_type(image_data)
            result = analyzer.analyze_image(image_data, mime)
            st.session_state.result = result
            st.session_state.image = image_data
        
        st.rerun()

if st.session_state.result and st.session_state.image:
    result = st.session_state.result
    img_data = st.session_state.image
    
    if isinstance(result, AnalysisError):
        st.markdown('<div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); padding: 2rem; border-radius: 20px; color: white; margin: 2rem 0;">' +
                    '<h2 style="margin: 0 0 1rem 0; font-weight: 700;">⚠️ Analysis Failed</h2>' +
                    f'<p style="font-size: 1.1rem; margin: 0;">{result.user_friendly_message}</p>' +
                    '</div>', unsafe_allow_html=True)
        
        if 'quota' in result.user_friendly_message.lower() or 'rate limit' in result.user_friendly_message.lower():
            st.info("🔗 Check API usage: https://aistudio.google.com/usage")
            st.caption("Wait a few minutes or upgrade your plan")
        elif 'api key' in result.user_friendly_message.lower() or '401' in result.message:
            st.warning("🔑 Check your .env file and verify GEMINI_API_KEY is set")
            st.caption("Get key at: https://aistudio.google.com/apikey")
        elif '404' in result.message or 'not found' in result.message.lower():
            st.warning(f"🔧 Model '{config.GEMINI_MODEL}' not available. Try gemini-2.5-flash")
        elif result.retry_suggested:
            st.info("💡 Tips: Clear photo • Good lighting • Single product")
        
        with st.expander("🔍 Technical Details"):
            st.code(f"Type: {result.error_type}\nMessage: {result.message}", language="text")
    
    elif isinstance(result, WaterFootprintAnalysis):
        st.session_state.total_water += result.total_liters
        st.session_state.total_carbon += getattr(result, 'carbon_kg', 0)
        st.session_state.history.append(result)
        
        metrics = WaterImpactMetrics.from_liters(result.total_liters)
        level, color, desc = get_impact_level(result.total_liters)
        
        st.markdown("---")
        
        col_img, col_info = st.columns([1, 2])
        
        with col_img:
            img = Image.open(io.BytesIO(img_data))
            st.image(img, caption="Analyzed Product", use_container_width=True)
        
        with col_info:
            icon = get_category_icon(result.product_category)
            badge = 'low' if level in ['Very Low', 'Low'] else 'medium' if level == 'Moderate' else 'high'
            
            st.markdown(
                f'<div class="product-card">'
                f'<h2 style="margin: 0; font-size: 2rem; font-weight: 700; color: #fff;">{icon} {result.product_name}</h2>'
                f'<p style="color: #a0a0a0; margin: 0.75rem 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px;">{result.product_category}</p>'
                f'<div class="impact-badge impact-{badge}" style="margin: 1rem 0;">{level} Impact</div>'
                f'<p style="color: #c0c0c0; margin-top: 1.5rem; line-height: 1.7; font-size: 0.95rem;">{desc}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            st.plotly_chart(create_confidence_indicator(result.confidence_score), use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("---")
        st.markdown('<div class="section-title">💧 Impact Metrics</div>', unsafe_allow_html=True)
        
        m1, m2, m3, m4, m5 = st.columns(5)
        
        m1.markdown(f'<div class="metric-card"><h3>Water</h3><div class="value">{result.total_liters:,.0f} L</div></div>', unsafe_allow_html=True)
        
        carbon = getattr(result, 'carbon_kg', 0)
        m2.markdown(f'<div class="metric-card"><h3>Carbon</h3><div class="value">{carbon:.1f} kg</div><small style="color: #9E9E9E;">CO₂ emissions</small></div>', unsafe_allow_html=True)
        
        comparison = get_relatable_comparison(result.total_liters)
        m3.markdown(f'<div class="metric-card"><h3>Equivalent</h3><div class="value" style="font-size: 1.2rem;">{comparison}</div></div>', unsafe_allow_html=True)
        
        m4.markdown(f'<div class="metric-card"><h3>Days of Water</h3><div class="value">{metrics.daily_drinking_equivalent:,.0f}</div><small style="color: #9E9E9E;">drinking water</small></div>', unsafe_allow_html=True)
        
        m5.markdown(f'<div class="metric-card"><h3>Savings</h3><div class="value" style="color: #4CAF50;">{result.sustainable_swap.savings_percentage:.0f}%</div><small style="color: #9E9E9E;">potential</small></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        v1, v2, v3 = st.columns(3)
        v1.plotly_chart(create_water_gauge(result.total_liters), use_container_width=True, config={'displayModeBar': False})
        v2.plotly_chart(create_water_breakdown_donut(result), use_container_width=True, config={'displayModeBar': False})
        if carbon > 0:
            v3.plotly_chart(create_carbon_footprint_chart(carbon, getattr(result.sustainable_swap, 'carbon_kg', 0)), use_container_width=True, config={'displayModeBar': False})
        
        if len(st.session_state.history) >= 2:
            st.markdown('<div class="section-title">📈 Your Impact Journey</div>', unsafe_allow_html=True)
            st.plotly_chart(create_cumulative_impact_chart(st.session_state.history), use_container_width=True, config={'displayModeBar': False})
        
        if hasattr(result, 'regional_impact') and result.regional_impact:
            st.markdown('<div class="section-title">🌍 Global Context</div>', unsafe_allow_html=True)
            regional_chart = create_regional_context_map(result.regional_impact)
            if regional_chart:
                col1, col2 = st.columns([2, 1])
                col1.plotly_chart(regional_chart, use_container_width=True, config={'displayModeBar': False})
                col2.markdown(f'<div class="metric-card"><h3>Regional Impact</h3><p style="color: #B0B0B0;">{result.regional_impact.context}</p></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">🔄 Real-World Comparison</div>', unsafe_allow_html=True)
        st.plotly_chart(create_impact_comparison_cards(metrics), use_container_width=True, config={'displayModeBar': False})
        
        st.markdown("---")
        st.markdown('<div class="section-title">🌱 Sustainable Alternative</div>', unsafe_allow_html=True)
        
        swap = result.sustainable_swap
        s1, s2 = st.columns([2, 1])
        
        s1.plotly_chart(create_comparison_bar_chart(
            result.product_name, result.total_liters,
            swap.product_name, swap.water_liters, swap.savings_percentage
        ), use_container_width=True, config={'displayModeBar': False})
        
        s2.markdown(
            f'<div class="swap-card">'
            f'<h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">🌿 Recommended Switch</h4>'
            f'<h3 style="margin: 0 0 1.5rem 0; font-size: 1.5rem; font-weight: 700;">{swap.product_name}</h3>'
            f'<div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">'
            f'<p style="margin: 0.5rem 0;"><strong>💧 Water:</strong> {swap.water_liters:,.0f}L <span style="color: #fff3cd;">(save {swap.savings_liters:,.0f}L)</span></p>'
            f'<p style="margin: 0.5rem 0;"><strong>🌍 CO₂:</strong> {getattr(swap, "carbon_kg", 0):.1f}kg <span style="color: #fff3cd;">(save {carbon - getattr(swap, "carbon_kg", 0):.1f}kg)</span></p>'
            f'</div>'
            f'<p style="margin: 0; opacity: 0.95; line-height: 1.6; font-size: 0.9rem;"><em>{swap.reasoning}</em></p>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        if hasattr(result, 'actionable_steps') and result.actionable_steps:
            st.markdown('<div class="section-title">✅ Take Action</div>', unsafe_allow_html=True)
            for i, step in enumerate(result.actionable_steps, 1):
                st.markdown(f'<div style="background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 12px; margin: 0.5rem 0; border-left: 3px solid #667eea;">'
                           f'<strong style="color: #667eea;">Step {i}:</strong> {step}'
                           f'</div>', unsafe_allow_html=True)
        
        if hasattr(result, 'collective_impact') and result.collective_impact:
            st.info(f"🌍 **Collective Power:** {result.collective_impact}")
        
        if result.fun_fact:
            st.markdown(
                f'<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 20px; color: white; margin: 2rem 0;">'
                f'<h4 style="margin: 0 0 1rem 0; font-size: 1.1rem; font-weight: 600; opacity: 0.9;">💡 Did You Know?</h4>'
                f'<p style="margin: 0; font-size: 1.05rem; line-height: 1.7;">{result.fun_fact}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        st.caption(f"📚 Source: {result.data_source}")
    
    st.markdown("---")
    if st.button("🔄 Scan Another", use_container_width=True):
        st.session_state.result = None
        st.session_state.image = None
        st.rerun()
