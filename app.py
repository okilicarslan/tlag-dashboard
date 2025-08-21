import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="TLAG Performance Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load sample data - will be replaced with Excel loader"""
    np.random.seed(42)
    
    # Sample data structure based on your Excel file
    stations = [f"İSTASYON_{i}" for i in range(1, 1154)]
    
    districts = ['ANKARA KUZEY BÖLGE', 'MARMARA BÖLGE', 'ADANA BÖLGE', 
                'CO BÖLGE', 'İSTANBUL BÖLGE', 'İZMİR BÖLGE', 'ANTALYA BÖLGE']
    
    segments = ['My Precious', 'Wasted Talent', 'Saboteur', 'Primitive']
    
    data = []
    for i, station in enumerate(stations):
        district = np.random.choice(districts)
        segment = np.random.choice(segments, p=[0.4, 0.3, 0.2, 0.1])
        
        current_score = np.random.uniform(0.3, 0.9)
        last_year_score = np.random.uniform(0.3, 0.9)
        difference = current_score - last_year_score
        
        data.append({
            'ROC': 1000 + i,
            'İstasyon': station,
            'DISTRICT': district,
            'SKOR': current_score,
            'GEÇEN_SENE_SKOR': last_year_score,
            'Fark': difference,
            'Site_Segment': segment,
            'TRANSACTION': np.random.randint(1000, 50000),
            'NOR_HEDEF': np.random.uniform(0.6, 0.7),
            'Geçerli': np.random.randint(10, 500)
        })
    
    return pd.DataFrame(data)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 TLAG PERFORMANCE INTELLIGENCE</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🎯 FİLTRELER")
    
    selected_districts = st.sidebar.multiselect(
        "Bölge Seçin:",
        options=df['DISTRICT'].unique(),
        default=df['DISTRICT'].unique()
    )
    
    selected_segments = st.sidebar.multiselect(
        "Segment Seçin:",
        options=df['Site_Segment'].unique(),
        default=df['Site_Segment'].unique()
    )
    
    score_range = st.sidebar.slider(
        "Skor Aralığı:",
        min_value=float(df['SKOR'].min()),
        max_value=float(df['SKOR'].max()),
        value=(float(df['SKOR'].min()), float(df['SKOR'].max()))
    )
    
    # Filter data
    filtered_df = df[
        (df['DISTRICT'].isin(selected_districts)) &
        (df['Site_Segment'].isin(selected_segments)) &
        (df['SKOR'] >= score_range[0]) &
        (df['SKOR'] <= score_range[1])
    ]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(filtered_df)}</h2>
            <p>Toplam İstasyon</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_score = filtered_df['SKOR'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h2>{avg_score:.3f}</h2>
            <p>Ortalama Skor</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        top_performers = len(filtered_df[filtered_df['Site_Segment'] == 'My Precious'])
        st.markdown(f"""
        <div class="metric-card">
            <h2>{top_performers}</h2>
            <p>My Precious</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        improvement_count = len(filtered_df[filtered_df['Fark'] > 0])
        st.markdown(f"""
        <div class="metric-card">
            <h2>{improvement_count}</h2>
            <p>Gelişen İstasyon</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance Distribution
    st.markdown("## 📊 PERFORMANS DAĞILIMI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segment performance
        fig1 = px.box(filtered_df, x='Site_Segment', y='SKOR', 
                     title="Segment Bazında Skor Dağılımı",
                     color='Site_Segment',
                     color_discrete_map={
                         'My Precious': '#2E8B57',
                         'Wasted Talent': '#DAA520', 
                         'Saboteur': '#DC143C',
                         'Primitive': '#708090'
                     })
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # District performance
        district_avg = filtered_df.groupby('DISTRICT')['SKOR'].mean().sort_values(ascending=False)
        fig2 = px.bar(x=district_avg.values, y=district_avg.index, 
                     orientation='h',
                     title="Bölge Bazında Ortalama Skor",
                     color=district_avg.values,
                     color_continuous_scale='Viridis')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Performance vs Transaction Analysis
    st.markdown("## 💰 PERFORMANS vs İŞLEM HACMİ ANALİZİ")
    
    fig3 = px.scatter(filtered_df, x='TRANSACTION', y='SKOR', 
                     color='Site_Segment', size='Geçerli',
                     hover_data=['İstasyon', 'DISTRICT'],
                     title="İşlem Hacmi vs Performans Korelasyonu",
                     color_discrete_map={
                         'My Precious': '#2E8B57',
                         'Wasted Talent': '#DAA520', 
                         'Saboteur': '#DC143C',
                         'Primitive': '#708090'
                     })
    fig3.update_layout(height=500)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Year over Year Comparison
    st.markdown("## 📈 YILLIK KARŞILAŞTIRMA ANALİZİ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance change distribution
        fig4 = px.histogram(filtered_df, x='Fark', nbins=30,
                           title="Performans Değişimi Dağılımı",
                           color_discrete_sequence=['#FF6B6B'])
        fig4.add_vline(x=0, line_dash="dash", line_color="red", 
                      annotation_text="Değişim Yok")
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        # Top/Bottom performers
        top_improvers = filtered_df.nlargest(10, 'Fark')[['İstasyon', 'Fark', 'SKOR']]
        worst_performers = filtered_df.nsmallest(10, 'Fark')[['İstasyon', 'Fark', 'SKOR']]
        
        st.markdown("### 🏆 EN ÇOK GELİŞENLER")
        st.dataframe(top_improvers, height=150)
        
        st.markdown("### ⚠️ EN ÇOK GERİLEYENLER")
        st.dataframe(worst_performers, height=150)
    
    # AI-Powered Insights
    st.markdown("## 🤖 AI-POWERED İÇGÖRÜLER")
    
    # Calculate insights
    total_stations = len(filtered_df)
    avg_improvement = filtered_df['Fark'].mean()
    best_district = filtered_df.groupby('DISTRICT')['SKOR'].mean().idxmax()
    worst_segment = filtered_df.groupby('Site_Segment')['SKOR'].mean().idxmin()
    
    insights = [
        f"📍 **En Başarılı Bölge:** {best_district} - Ortalama skor: {filtered_df[filtered_df['DISTRICT']==best_district]['SKOR'].mean():.3f}",
        f"⚡ **Dikkat Gereken Segment:** {worst_segment} segmenti optimize edilmeli",
        f"📊 **Genel Trend:** {'Pozitif' if avg_improvement > 0 else 'Negatif'} - Ortalama değişim: {avg_improvement:.3f}",
        f"🎯 **Aksiyon Önerisi:** {len(filtered_df[filtered_df['Site_Segment']=='Saboteur'])} adet 'Saboteur' istasyon acil müdahale gerektiriyor"
    ]
    
    for insight in insights:
        st.markdown(f"""
        <div class="insight-box">
            {insight}
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Data Table
    st.markdown("## 📋 DETAY VERİ TABLOSU")
    
    # Add search functionality
    search_term = st.text_input("İstasyon Ara:", placeholder="İstasyon adı yazın...")
    
    if search_term:
        display_df = filtered_df[filtered_df['İstasyon'].str.contains(search_term, case=False, na=False)]
    else:
        display_df = filtered_df
    
    # Style the dataframe
    styled_df = display_df.style.format({
        'SKOR': '{:.3f}',
        'GEÇEN_SENE_SKOR': '{:.3f}',
        'Fark': '{:.3f}',
        'NOR_HEDEF': '{:.3f}'
    }).background_gradient(subset=['SKOR'], cmap='RdYlGn')
    
    st.dataframe(styled_df, height=400)
    
    # Export functionality
    st.markdown("## 💾 VERİ İNDİRME")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 CSV İndir",
            data=csv,
            file_name=f"tlag_performance_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Create summary report
        summary_data = {
            'Metrik': ['Toplam İstasyon', 'Ortalama Skor', 'En İyi Bölge', 'Gelişme Oranı'],
            'Değer': [
                len(filtered_df),
                f"{filtered_df['SKOR'].mean():.3f}",
                best_district,
                f"{(filtered_df['Fark'] > 0).mean()*100:.1f}%"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_csv = summary_df.to_csv(index=False)
        
        st.download_button(
            label="📊 Özet Rapor İndir",
            data=summary_csv,
            file_name=f"tlag_summary_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()