import streamlit as st
import pandas as pd
import requests
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import uuid

# تحديد عنوان الـ API (سيتم ضبطه لاحقًا على Railway)
FASTAPI_URL = os.getenv("FASTAPI_URL", "https://car-fault-prediction-production.up.railway.app/predict/")

# Streamlit configuration
st.set_page_config(
    page_title="Advanced Vehicle Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern automotive look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #0f172a;
        --primary-light: #1e293b;
        --secondary: #f97316;
        --accent: #3b82f6;
        --text-light: #f8fafc;
        --text-dark: #1e293b;
        --background: #f1f5f9;
        --card-bg: #ffffff;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #0ea5e9;
    }
    
    * {
        font-family: 'Montserrat', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: var(--text-light);
        padding: 0;
    }
    
    /* Main container */
    .stApp {
        max-width: 100%;
        margin: 0;
        background: var(--background);
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 2rem 3rem;
        border-radius: 0;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .dashboard-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?ixlib=rb-1.2.1&auto=format&fit=crop&w=1567&q=80');
        background-size: cover;
        background-position: center;
        opacity: 0.15;
        z-index: 0;
    }
    
    .dashboard-header h1 {
        color: var(--text-light);
        font-weight: 700;
        font-size: 3rem !important;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .dashboard-header p {
        color: var(--text-light);
        font-size: 1.2rem !important;
        opacity: 0.9;
        max-width: 800px;
        position: relative;
        z-index: 1;
    }
    
    /* Card styling */
    .card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid var(--accent);
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
    }
    
    .card h2, .card h3, .card h4 {
        color: var(--primary);
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Upload area styling */
    .upload-area {
        background: var(--card-bg);
        border: 2px dashed var(--accent);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: var(--secondary);
        background-color: rgba(59, 130, 246, 0.05);
    }
    
    /* File uploader styling */
    .css-1cpxqw2 {
        background-color: rgba(15, 23, 42, 0.03) !important;
        border: none !important;
        border-radius: 8px !important;
        color: var(--primary) !important;
        padding: 1rem !important;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, var(--accent) 0%, #60a5fa 100%);
        color: var(--text-light);
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: var(--card-bg);
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    .stSelectbox > div > div > div {
        color: var(--text-dark);
        font-weight: 500;
    }
    
    /* Chart selection styling */
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1rem;
    }
    
    .chart-option {
        background: var(--card-bg);
        border-radius: 10px;
        padding: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .chart-option:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-color: var(--accent);
    }
    
    .chart-option h4 {
        color: var(--primary);
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .chart-option p {
        color: var(--text-dark);
        opacity: 0.8;
        flex-grow: 1;
    }
    
    .chart-option.selected {
        border: 2px solid var(--accent);
        background-color: rgba(59, 130, 246, 0.05);
    }
    
    /* Dataframe styling */
    .dataframe {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .dataframe th {
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
        color: var(--text-light);
        padding: 12px 15px;
        text-align: left;
        font-weight: 600;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    
    .dataframe td {
        padding: 12px 15px;
        border-bottom: 1px solid #e2e8f0;
        color: var(--text-dark);
    }
    
    .dataframe tr:last-child td {
        border-bottom: none;
    }
    
    .dataframe tr:nth-child(even) {
        background-color: rgba(241, 245, 249, 0.5);
    }
    
    .dataframe tr:hover td {
        background-color: rgba(59, 130, 246, 0.05);
    }
    
    /* Fault indicators */
    .fault-indicator {
        padding: 0.5rem 1rem;
        border-radius: 30px;
        font-weight: 600;
        display: inline-block;
        text-align: center;
        min-width: 120px;
    }
    
    .no-fault {
        background-color: rgba(16, 185, 129, 0.1);
        color: var(--success);
        border: 1px solid var(--success);
    }
    
    .engine-fault {
        background-color: rgba(245, 158, 11, 0.1);
        color: var(--warning);
        border: 1px solid var(--warning);
    }
    
    .electrical-fault {
        background-color: rgba(59, 130, 246, 0.1);
        color: var(--accent);
        border: 1px solid var(--accent);
    }
    
    .emission-fault {
        background-color: rgba(139, 92, 246, 0.1);
        color: #8b5cf6;
        border: 1px solid #8b5cf6;
    }
    
    .transmission-fault {
        background-color: rgba(239, 68, 68, 0.1);
        color: var(--danger);
        border: 1px solid var(--danger);
    }
    
    /* Charts container */
    .chart-container {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border-left: 5px solid var(--accent);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: var(--text-dark);
        font-weight: 500;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--card-bg);
        color: var(--accent);
        font-weight: 600;
        border-bottom: none;
        border-top: 3px solid var(--accent);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
        border: none;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--accent) !important;
    }
    
    /* Dashboard sections */
    .dashboard-section {
        margin-bottom: 2rem;
    }
    
    /* Footer styling */
    .dashboard-footer {
        background: var(--primary-light);
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
        border-radius: 12px;
        color: var(--text-light);
    }
    
    /* Vehicle status indicators */
    .status-indicators {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .status-indicator {
        background: var(--card-bg);
        border-radius: 10px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex: 1;
        min-width: 150px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-bottom: 3px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .status-indicator:hover {
        transform: translateY(-5px);
    }
    
    .status-indicator h3 {
        font-size: 1rem;
        color: var(--text-dark);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .status-indicator p {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: var(--primary);
    }
    
    .status-indicator.critical {
        border-bottom-color: var(--danger);
    }
    
    .status-indicator.warning {
        border-bottom-color: var(--warning);
    }
    
    .status-indicator.normal {
        border-bottom-color: var(--success);
    }
    
    .status-indicator.info {
        border-bottom-color: var(--accent);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: var(--accent);
    }
    
    /* Dark mode elements */
    .dark-card {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: var(--text-light);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    }
    
    .dark-card h2, .dark-card h3 {
        color: var(--text-light);
    }
    
    /* Arabic text direction */
    .rtl-text {
        direction: rtl;
        text-align: right;
    }
    
    /* Modern badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background-color: var(--accent);
        color: white;
    }
    
    .badge-secondary {
        background-color: var(--secondary);
        color: white;
    }
    
    /* Chart legend styling */
    .custom-legend {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        padding: 0.5rem 0;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .legend-color {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard header with car illustration
st.markdown('''
<div class="dashboard-header">
    <h1>🚗 Advanced Vehicle Analytics</h1>
    <p>A comprehensive diagnostic platform for real-time vehicle data analysis and fault prediction</p>
</div>
''', unsafe_allow_html=True)

# Description of charts
chart_descriptions = {
    "1. Histogram of Engine RPM": "رسم بياني يوضح توزيع دورات المحرك، مع تمييز الدورات العالية والمنخفضة",
    "2. Line Graph of Engine RPM over time": "مخطط زمني يظهر تغيرات دورات المحرك مع الوقت، مع تمييز ملون للدورات العالية",
    "3. Line Graph of Coolant Temperature": "مخطط درجة حرارة سائل التبريد على مدار الزمن، مع خط تحذير عند 105 درجة مئوية",
    "4. Histogram of Oil Temperature": "رسم بياني يوضح توزيع درجات حرارة الزيت مع إظهار المتوسط والوسيط",
    "5. Line Graph of Oil Temperature": "مخطط زمني يظهر تغيرات درجة حرارة الزيت على مدار اليوم",
    "6. Line Graph of Engine RPM and Oil Temperature": "مخطط مزدوج يظهر العلاقة بين دورات المحرك ودرجة حرارة الزيت",
    "7. Line Graph of Engine Load Percent & RPM": "مخطط مزدوج يظهر العلاقة بين حمل المحرك ودوراته",
    "8. Histogram of Battery Voltage": "رسم بياني يوضح توزيع قيم جهد البطارية",
    "9. Line Graph of Battery Voltage": "مخطط زمني يظهر تغيرات جهد البطارية على مدار اليوم",
    "10. Line Graph of Manifold Absolute Pressure": "مخطط ضغط الهواء داخل مشعب السحب (MAP) مقاساً بالكيلو باسكال",
    "11. Line Graph of Mass Air Flow": "مخطط زمني لتدفق كتلة الهواء (MAF) مقاساً بالجرام في الثانية",
    "12. 3D Scatter Plot of Engine Parameters": "رسم ثلاثي الأبعاد يوضح العلاقة بين دورات المحرك وتوقيت الإشعال وضغط مشعب السحب",
    "13. Line Graph of Exhaust Gas Recirculation": "مخطط زمني لحالة نظام إعادة تدوير غاز العادم (EGR)",
    "14. Line Graph of Catalytic Converter Efficiency": "مخطط زمني يوضح كفاءة عمل المحول الحفاز",
    "15. Line Graph of Brake Status": "مخطط زمني يوضح حالة الفرامل",
    "16. Line Graph of Tire Pressure": "مخطط زمني يوضح ضغط الإطارات بالـ PSI",
    "17. Line Graph of Ambient Temperature": "مخطط زمني يوضح درجة الحرارة المحيطة بالمركبة"
}

# Upload file section
st.markdown('<div class="upload-container">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h2 style='text-align: center;'>رفع ملف البيانات</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a file containing vehicle data", type="csv")

with col2:
    st.markdown("<h2 style='text-align: center;'>File info</h2>", unsafe_allow_html=True)
    if uploaded_file is not None:
        st.success("✅ uploaded successfully!")
        st.info("The file will be sent to the API for processing.")
    else:
        st.warning("⚠️ The file has not been uploaded yet!")

st.markdown('</div>', unsafe_allow_html=True)

# التحقق من رفع الملف
df = None
if uploaded_file is not None:
    with st.spinner("🔄 جاري إرسال الملف ومعالجته عبر API..."):
        try:
            # إرسال الملف إلى الـ API
            files = {'file': (uploaded_file.name, uploaded_file, 'text/csv')}
            response = requests.post(FASTAPI_URL, files=files)

            # التحقق من استجابة الـ API
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    df = pd.DataFrame(result["results"])
                    st.success("✅ تمت المعالجة والتنبؤ بنجاح!")
                    st.subheader("📋 أنواع الأعطال المحتملة الحدوث")

                    # عرض التنبؤات
                    fault_types = ['كل الأنواع'] + list(df['Predicted_Fault'].unique())
                    selected_fault = st.selectbox("اختر نوع العطل لعرضه:", fault_types)

                    if selected_fault != 'كل الأنواع':
                        filtered_df = df[df['Predicted_Fault'] == selected_fault]
                    else:
                        filtered_df = df

                    # عرض النتائج
                    if not filtered_df.empty:
                        table_data = []
                        for idx, row in filtered_df.iterrows():
                            fault_icon = {
                                'No Fault': '✅',
                                'Engine Fault': '⚠️',
                                'Electrical Fault': '⚠️',
                                'Emission Fault': '⚠️',
                                'Transmission Fault': '⚠️'
                            }.get(row['Predicted_Fault'], '❓')

                            table_data.append({
                                "Recording": f"{fault_icon} {idx + 1}",
                                "Possible fault type": row['Predicted_Fault'],
                                "Attention": row['Prediction_Message'],
                            })

                        table_df = pd.DataFrame(table_data)
                        st.dataframe(table_df, use_container_width=True)

                        # زر لتحميل النتائج كملف CSV
                        csv = table_df.to_csv(index=False)
                        st.download_button(
                            label="تحميل النتائج كملف CSV",
                            data=csv,
                            file_name="fault_predictions.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("لا توجد نتائج لعرضها.")
                else:
                    st.error(f"❌ حدث خطأ من الخادم: {result.get('error')}")
            else:
                st.error(f"❌ حدث خطأ من الخادم: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء إرسال الملف أو المعالجة: {str(e)}")


# معالجة الرسوم البيانية فقط إذا كان df موجودًا
if df is not None:
    try:
        # تحويل الوقت إلى تنسيق التاريخ
        if 'Timestamp' in df.columns:
            try:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df['Date'] = df['Timestamp'].dt.date
            except:
                st.warning("خطأ في تحويل Timestamp إلى تنسيق التاريخ")

        st.markdown("<h2 style='text-align: center;'>--Select the charts you want to view--</h2>", unsafe_allow_html=True)

        st.markdown('<div class="chart-options-grid">', unsafe_allow_html=True)

        selected_charts = {}

        col_count = 3  # عدد الأعمدة في كل صف
        chart_items = list(chart_descriptions.items())
        rows = [chart_items[i:i+col_count] for i in range(0, len(chart_items), col_count)]

        for row in rows:
            cols = st.columns(col_count)
            for i, (chart_name, chart_desc) in enumerate(row):
                with cols[i]:
                    st.markdown(f"""
                    <div class="chart-option">
                        <h4>{chart_name}</h4>
                        <p>{chart_desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    selected_charts[chart_name] = st.checkbox("عرض", key=f"chart_{chart_name}")

        st.markdown('</div>', unsafe_allow_html=True)

        if any(selected_charts.values()):
            st.markdown("<h2 style='text-align: center;'>Charts of Vehicle</h2>", unsafe_allow_html=True)

            charts_to_show = [chart for chart, selected in selected_charts.items() if selected]
            rows = [charts_to_show[i:i+2] for i in range(0, len(charts_to_show), 2)]

            for row in rows:
                cols = st.columns([1, 1])
                for i, chart_name in enumerate(row):
                    with cols[i]:
                        st.markdown(f'<div class="chart-container"><h3>{chart_name}</h3>', unsafe_allow_html=True)

                        # الرسم البياني حسب النوع
                        if chart_name == "1. Histogram of Engine RPM":
                            if 'Engine_RPM' in df.columns:
                                rpm_threshold = 6000
                                normal_rpm = df[df['Engine_RPM'] <= rpm_threshold]
                                high_rpm = df[df['Engine_RPM'] > rpm_threshold]

                                fig = go.Figure()
                                fig.add_trace(go.Histogram(
                                    x=normal_rpm['Engine_RPM'],
                                    nbinsx=50,
                                    name='دورات عادية',
                                    marker_color='green',
                                    opacity=0.75
                                ))
                                fig.add_trace(go.Histogram(
                                    x=high_rpm['Engine_RPM'],
                                    nbinsx=50,
                                    name='دورات عالية',
                                    marker_color='red',
                                    opacity=0.75
                                ))

                                fig.update_layout(
                                    title='توزيع دورات المحرك',
                                    xaxis_title='دورات المحرك (RPM)',
                                    yaxis_title='العدد',
                                    barmode='overlay',
                                    template='plotly_white',
                                    height=400,
                                    legend=dict(title='فئة الدورات')
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود Engine_RPM غير موجود في البيانات")

                        elif chart_name == "2. Line Graph of Engine RPM over time":
                            if 'Engine_RPM' in df.columns and 'Timestamp' in df.columns:
                                traces = []

                                for i in range(len(df) - 1):
                                    x_segment = [df["Timestamp"].iloc[i], df["Timestamp"].iloc[i+1]]
                                    y_segment = [df["Engine_RPM"].iloc[i], df["Engine_RPM"].iloc[i+1]]

                                    color = 'orangered' if y_segment[0] > 6500 or y_segment[1] > 6500 else 'seagreen'

                                    traces.append(go.Scatter(
                                        x=x_segment,
                                        y=y_segment,
                                        mode='lines',
                                        line=dict(color=color, width=3),
                                        showlegend=False
                                    ))

                                fig = go.Figure(data=traces)
                                fig.update_layout(
                                    title="دورات المحرك عبر الزمن",
                                    xaxis_title="الوقت",
                                    yaxis_title="دورات المحرك (RPM)",
                                    xaxis=dict(
                                        tickformat="%H:%M:%S",
                                        tickangle=45
                                    ),
                                    template="plotly_white",
                                    height=400
                                )

                                fig.update_xaxes(showgrid=True, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("بعض الأعمدة المطلوبة غير موجودة في البيانات")

                        elif chart_name == "3. Line Graph of Coolant Temperature":
                            if 'Coolant_Temp_C' in df.columns and 'Timestamp' in df.columns and 'Date' in df.columns:
                                unique_days = df['Date'].unique()

                                if len(unique_days) > 0:
                                    day = unique_days[0]  # عرض اليوم الأول فقط
                                    day_data = df[df['Date'] == day].sort_values('Timestamp')

                                    fig = go.Figure()

                                    for i in range(len(day_data) - 1):
                                        x_segment = [day_data['Timestamp'].iloc[i], day_data['Timestamp'].iloc[i+1]]
                                        y_segment = [day_data['Coolant_Temp_C'].iloc[i], day_data['Coolant_Temp_C'].iloc[i+1]]

                                        color = 'orangered' if y_segment[0] > 105 or y_segment[1] > 105 else 'seagreen'

                                        fig.add_trace(go.Scatter(
                                            x=x_segment,
                                            y=y_segment,
                                            mode='lines',
                                            line=dict(color=color, width=3),
                                            showlegend=False
                                        ))

                                    fig.add_shape(
                                        type='line',
                                        x0=day_data['Timestamp'].min(),
                                        x1=day_data['Timestamp'].max(),
                                        y0=105,
                                        y1=105,
                                        line=dict(color='red', width=2, dash='dash'),
                                    )

                                    fig.update_layout(
                                        title=f'درجة حرارة سائل التبريد بتاريخ {day}',
                                        xaxis_title='الوقت',
                                        yaxis_title='درجة حرارة سائل التبريد (°C)',
                                        xaxis=dict(tickangle=45),
                                        template='plotly_white',
                                        height=400,
                                    )

                                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.error("لم يتم العثور على بيانات التاريخ")
                            else:
                                st.error("بعض الأعمدة المطلوبة غير موجودة في البيانات")

                        elif chart_name == "4. Histogram of Oil Temperature":
                            if 'Oil_Temp_C' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Histogram(
                                    x=df['Oil_Temp_C'],
                                    nbinsx=30,
                                    marker_color='orange',
                                    opacity=0.6,
                                    name='توزيع درجة حرارة الزيت'
                                ))

                                fig.add_shape(
                                    type='line',
                                    x0=df['Oil_Temp_C'].mean(),
                                    x1=df['Oil_Temp_C'].mean(),
                                    y0=0,
                                    y1=1,
                                    yref='paper',
                                    line=dict(color='blue', width=2, dash='dash'),
                                    name='المتوسط'
                                )

                                fig.add_shape(
                                    type='line',
                                    x0=df['Oil_Temp_C'].median(),
                                    x1=df['Oil_Temp_C'].median(),
                                    y0=0,
                                    y1=1,
                                    yref='paper',
                                    line=dict(color='green', width=2, dash='dash'),
                                    name='الوسيط'
                                )

                                fig.update_layout(
                                    title='توزيع درجة حرارة الزيت (°C)',
                                    xaxis_title='درجة حرارة الزيت (°C)',
                                    yaxis_title='التكرار',
                                    template='plotly_white',
                                    height=400,
                                    legend=dict(
                                        y=0.99,
                                        x=0.01,
                                        title_text=''
                                    )
                                )

                                fig.add_annotation(
                                    x=df['Oil_Temp_C'].mean(),
                                    y=0.95,
                                    yref='paper',
                                    text=f"المتوسط: {df['Oil_Temp_C'].mean():.1f}°C",
                                    showarrow=True,
                                    arrowhead=1,
                                    ax=50,
                                    ay=-30
                                )

                                fig.add_annotation(
                                    x=df['Oil_Temp_C'].median(),
                                    y=0.85,
                                    yref='paper',
                                    text=f"الوسيط: {df['Oil_Temp_C'].median():.1f}°C",
                                    showarrow=True,
                                    arrowhead=1,
                                    ax=-50,
                                    ay=-30
                                )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود Oil_Temp_C غير موجود في البيانات")

                        elif chart_name == "5. Line Graph of Oil Temperature":
                            if 'Oil_Temp_C' in df.columns and 'Timestamp' in df.columns and 'Date' in df.columns:
                                unique_days = df['Date'].unique()

                                if len(unique_days) > 0:
                                    day = unique_days[0]  # عرض اليوم الأول فقط
                                    day_data = df[df['Date'] == day].sort_values('Timestamp')

                                    fig = go.Figure()

                                    fig.add_trace(
                                        go.Scatter(
                                            x=day_data['Timestamp'],
                                            y=day_data['Oil_Temp_C'],
                                            mode='lines+markers',
                                            line=dict(color='darkorange', width=3),
                                            name='درجة حرارة الزيت'
                                        )
                                    )

                                    fig.update_layout(
                                        title=f'درجة حرارة الزيت (°C) بتاريخ {day}',
                                        xaxis_title='الوقت',
                                        yaxis_title='درجة حرارة الزيت (°C)',
                                        xaxis=dict(tickangle=50),
                                        template='plotly_white',
                                        height=400,
                                    )

                                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.error("لم يتم العثور على بيانات التاريخ")
                            else:
                                st.error("بعض الأعمدة المطلوبة غير موجودة في البيانات")

                        elif chart_name == "6. Line Graph of Engine RPM and Oil Temperature":
                            if all(col in df.columns for col in ['Engine_RPM', 'Oil_Temp_C', 'Timestamp']):
                                fig = make_subplots(specs=[[{"secondary_y": True}]])

                                fig.add_trace(
                                    go.Scatter(
                                        x=df["Timestamp"],
                                        y=df["Engine_RPM"],
                                        mode='lines+markers',
                                        name='دورات المحرك',
                                        line=dict(color='darkgreen', width=3),
                                        marker=dict(size=7)
                                    ),
                                    secondary_y=False
                                )

                                fig.add_trace(
                                    go.Scatter(
                                        x=df["Timestamp"],
                                        y=df["Oil_Temp_C"],
                                        mode='lines+markers',
                                        name='درجة حرارة الزيت',
                                        line=dict(color='darkorange', width=3),
                                        marker=dict(size=7)
                                    ),
                                    secondary_y=True
                                )

                                fig.update_layout(
                                    title="العلاقة بين دورات المحرك ودرجة حرارة الزيت",
                                    xaxis_title="الوقت",
                                    template="plotly_white",
                                    height=400,
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=1.02,
                                        xanchor="right",
                                        x=1
                                    )
                                )

                                fig.update_yaxes(title_text="دورات المحرك (RPM)", secondary_y=False, color="darkgreen")
                                fig.update_yaxes(title_text="درجة حرارة الزيت (°C)", secondary_y=True, color="darkorange")

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("بعض الأعمدة المطلوبة غير موجودة في البيانات")

                        elif chart_name == "7. Line Graph of Engine Load Percent & RPM":
                            if all(col in df.columns for col in ['Engine_RPM', 'Engine_Load_Percent', 'Timestamp']):
                                fig = make_subplots(specs=[[{"secondary_y": True}]])

                                fig.add_trace(
                                    go.Scatter(
                                        x=df["Timestamp"],
                                        y=df["Engine_RPM"],
                                        mode='lines',
                                        name='دورات المحرك',
                                        line=dict(color='chocolate', width=3),
                                    ),
                                    secondary_y=False
                                )

                                fig.add_trace(
                                    go.Scatter(
                                        x=df["Timestamp"],
                                        y=df["Engine_Load_Percent"],
                                        mode='lines',
                                        name='حمل المحرك (%)',
                                        line=dict(color='blue', width=3),
                                    ),
                                    secondary_y=True
                                )

                                fig.update_layout(
                                    title="العلاقة بين دورات المحرك ونسبة الحمل",
                                    xaxis_title="الوقت",
                                    template="plotly_white",
                                    height=400,
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=1.02,
                                        xanchor="right",
                                        x=1
                                    )
                                )

                                fig.update_yaxes(title_text="دورات المحرك (RPM)", secondary_y=False, color="chocolate")
                                fig.update_yaxes(title_text="نسبة حمل المحرك (%)", secondary_y=True, color="blue")

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("بعض الأعمدة المطلوبة غير موجودة في البيانات")

                        elif chart_name == "8. Histogram of Battery Voltage":
                            if 'Battery_Voltage_V' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Histogram(
                                    x=df['Battery_Voltage_V'],
                                    nbinsx=30,
                                    marker_color='green',
                                    opacity=0.75,
                                    name='توزيع جهد البطارية'
                                ))

                                fig.update_layout(
                                    title="توزيع جهد البطارية",
                                    xaxis_title="جهد البطارية (فولت)",
                                    yaxis_title="التكرار",
                                    template="plotly_white",
                                    height=400
                                )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود Battery_Voltage_V غير موجود في البيانات")

                        elif chart_name == "9. Line Graph of Battery Voltage":
                            if 'Battery_Voltage_V' in df.columns and 'Timestamp' in df.columns and 'Date' in df.columns:
                                unique_days = df['Date'].unique()

                                if len(unique_days) > 0:
                                    day = unique_days[0]  # عرض اليوم الأول فقط
                                    day_data = df[df['Date'] == day].sort_values('Timestamp')

                                    fig = go.Figure()

                                    fig.add_trace(
                                        go.Scatter(
                                            x=day_data['Timestamp'],
                                            y=day_data['Battery_Voltage_V'],
                                            mode='lines+markers',
                                            line=dict(color='teal', width=3),
                                            name='جهد البطارية'
                                        )
                                    )

                                    fig.update_layout(
                                        title=f'جهد البطارية بتاريخ {day}',
                                        xaxis_title='الوقت',
                                        yaxis_title='جهد البطارية (فولت)',
                                        xaxis=dict(tickangle=50),
                                        template='plotly_white',
                                        height=400,
                                    )

                                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.error("لم يتم العثور على بيانات التاريخ")
                            else:
                                st.error("بعض الأعمدة المطلوبة غير موجودة في البيانات")

                        elif chart_name == "10. Line Graph of Manifold Absolute Pressure":
                            if 'MAP_kPa' in df.columns and 'Timestamp' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Scatter(
                                    x=df['Timestamp'],
                                    y=df['MAP_kPa'],
                                    mode='lines',
                                    marker=dict(size=7, color='purple'),
                                    line=dict(width=3, color='purple'),
                                    name='ضغط مشعب السحب'
                                ))

                                fig.update_layout(
                                    title="ضغط الهواء داخل مشعب السحب (MAP_kPa)",
                                    xaxis_title="الوقت",
                                    yaxis_title="الضغط (كيلو باسكال)",
                                    template="plotly_white",
                                    height=400,
                                    xaxis=dict(tickangle=45)
                                )

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود MAP_kPa غير موجود في البيانات")

                        elif chart_name == "11. Line Graph of Mass Air Flow":
                            if 'MAF_gps' in df.columns and 'Timestamp' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Sc芦atter(
                                    x=df['Timestamp'],
                                    y=df['MAF_gps'],
                                    mode='lines',
                                    marker=dict(size=7, color='green'),
                                    line=dict(width=3, color='green'),
                                    name='تدفق كتلة الهواء'
                                ))

                                fig.update_layout(
                                    title="💨 تدفق كتلة الهواء (جرام/ثانية)",
                                    xaxis_title="الوقت",
                                    yaxis_title="تدفق كتلة الهواء (جرام/ثانية)",
                                    template="plotly_white",
                                    height=400,
                                    xaxis=dict(tickangle=45)
                                )

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود MAF_gps غير موجود في البيانات")

                        elif chart_name == "12. 3D Scatter Plot of Engine Parameters":
                            if all(col in df.columns for col in ['Engine_RPM', 'Ignition_Timing_Deg', 'MAP_kPa', 'MAF_gps']):
                                fig = px.scatter_3d(
                                    data_frame=df,
                                    x="Engine_RPM",
                                    y="Ignition_Timing_Deg",
                                    z="MAP_kPa",
                                    color="MAF_gps",
                                    title="عرض ثلاثي الأبعاد: دورات المحرك مقابل توقيت الإشعال مقابل ضغط المشعب (ملون حسب تدفق الهواء)",
                                    labels={
                                        "Engine_RPM": "دورات المحرك (RPM)",
                                        "Ignition_Timing_Deg": "توقيت الإشعال (درجة)",
                                        "MAP_kPa": "ضغط المشعب (كيلو باسكال)",
                                        "MAF_gps": "تدفق كتلة الهواء (جرام/ثانية)"
                                    }
                                )

                                fig.update_layout(
                                    height=600,
                                    template="plotly_white"
                                )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("بعض الأعمدة المطلوبة غير موجودة في البيانات")

                        elif chart_name == "13. Line Graph of Exhaust Gas Recirculation":
                            if 'EGR_Status' in df.columns and 'Timestamp' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Scatter(
                                    x=df['Timestamp'],
                                    y=df['EGR_Status'],
                                    mode='lines',
                                    marker=dict(size=7, color='royalblue'),
                                    line=dict(width=3, color='royalblue'),
                                    name='حالة EGR'
                                ))

                                fig.update_layout(
                                    title="حالة نظام إعادة تدوير غاز العادم (EGR)",
                                    xaxis_title="الوقت",
                                    yaxis_title="حالة EGR (مشفرة)",
                                    template="plotly_white",
                                    height=400,
                                    xaxis=dict(tickangle=45)
                                )

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود EGR_Status غير موجود في البيانات")

                        elif chart_name == "14. Line Graph of Catalytic Converter Efficiency":
                            if 'Catalytic_Converter_Percent' in df.columns and 'Timestamp' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Scatter(
                                    x=df['Timestamp'],
                                    y=df['Catalytic_Converter_Percent'],
                                    mode='lines',
                                    marker=dict(size=7, color='teal'),
                                    line=dict(width=3, color='teal'),
                                    name='كفاءة المحول الحفاز'
                                ))

                                fig.update_layout(
                                    title="كفاءة عمل المحول الحفاز",
                                    xaxis_title="الوقت",
                                    yaxis_title="كفاءة المحول الحفاز (%)",
                                    template="plotly_white",
                                    height=400,
                                    xaxis=dict(tickangle=45)
                                )

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود Catalytic_Converter_Percent غير موجود في البيانات")

                        elif chart_name == "15. Line Graph of Brake Status":
                            if 'Brake_Status' in df.columns and 'Timestamp' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Scatter(
                                    x=df['Timestamp'],
                                    y=df['Brake_Status'],
                                    mode='lines',
                                    marker=dict(size=7, color='royalblue'),
                                    line=dict(width=3, color='royalblue'),
                                    name='حالة الفرامل'
                                ))

                                fig.update_layout(
                                    title="حالة الفرامل",
                                    xaxis_title="الوقت",
                                    yaxis_title="حالة الفرامل",
                                    template="plotly_white",
                                    height=400,
                                    xaxis=dict(tickangle=45)
                                )

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود Brake_Status غير موجود في البيانات")

                        elif chart_name == "16. Line Graph of Tire Pressure":
                            if 'Tire_Pressure_psi' in df.columns and 'Timestamp' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Scatter(
                                    x=df['Timestamp'],
                                    y=df['Tire_Pressure_psi'],
                                    mode='lines',
                                    marker=dict(size=7, color='indigo'),
                                    line=dict(width=3, color='indigo'),
                                    name='ضغط الإطارات'
                                ))

                                fig.update_layout(
                                    title="ضغط إطارات المركبة",
                                    xaxis_title="الوقت",
                                    yaxis_title="ضغط الإطارات (PSI)",
                                    template="plotly_white",
                                    height=400,
                                    xaxis=dict(tickangle=45)
                                )

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود Tire_Pressure_psi غير موجود في البيانات")

                        elif chart_name == "17. Line Graph of Ambient Temperature":
                            if 'Ambient_Temp_C' in df.columns and 'Timestamp' in df.columns:
                                fig = go.Figure()

                                fig.add_trace(go.Scatter(
                                    x=df['Timestamp'],
                                    y=df['Ambient_Temp_C'],
                                    mode='lines',
                                    marker=dict(size=7, color='goldenrod'),
                                    line=dict(width=3, color='goldenrod'),
                                    name='درجة الحرارة المحيطة'
                                ))

                                fig.update_layout(
                                    title="درجة الحرارة المحيطة بالمركبة",
                                    xaxis_title="الوقت",
                                    yaxis_title="درجة الحرارة (°C)",
                                    template="plotly_white",
                                    height=400,
                                    xaxis=dict(tickangle=45)
                                )

                                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
                                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error("عمود Ambient_Temp_C غير موجود في البيانات")

                        st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("--Choose the charts you want to view--")

    except Exception as e:
        st.error(f"خطأ: {str(e)}")

else:
    st.markdown("<div style='text-align: center; padding: 3rem;'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #34495e; padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-top: 2rem;">
        <p>2025 | Teem OHI | Vehicle Dashboard | Vehicle Charts ©</p>
    </div>
    """, unsafe_allow_html=True)
#---------------------------------------------------------------------
