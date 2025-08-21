import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import openpyxl
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="TLAG Multi-Period Analysis Dashboard",
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
    .comparison-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .file-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    .trend-positive {
        color: #2ecc71;
        font-weight: bold;
    }
    .trend-negative {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for file management
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []

@st.cache_data
def load_excel_data(uploaded_file, file_name):
    """Load and process Excel data"""
    try:
        df = pd.read_excel(uploaded_file, sheet_name="TLAG DOKUNMA (2)")
        df.columns = df.columns.str.strip()
        
        # Clean and process data
        df = df.dropna(subset=['ROC', 'İstasyon'])
        
        # Ensure numeric columns
        numeric_columns = ['ROC', 'NOR HEDEF', 'DISTRICT HEDEF', 'SKOR', 'GEÇEN SENE SKOR', 'Fark', 'Geçerli', 'TRANSACTION']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Add file identifier and timestamp
        df['Dosya_Adı'] = file_name
        df['Yükleme_Tarihi'] = datetime.now()
        
        return df
    except Exception as e:
        st.error(f"Dosya okuma hatası: {str(e)}")
        return None

def generate_sample_data(file_name, period_offset=0):
    """Generate sample data for testing"""
    np.random.seed(42 + period_offset)
    
    stations = [f"İSTASYON_{i}" for i in range(1, 1154)]
    districts = ['ANKARA KUZEY BÖLGE', 'MARMARA BÖLGE', 'ADANA BÖLGE', 
                'CO BÖLGE', 'İSTANBUL BÖLGE', 'İZMİR BÖLGE', 'ANTALYA BÖLGE']
    segments = ['My Precious', 'Wasted Talent', 'Saboteur', 'Primitive']
    
    data = []
    for i, station in enumerate(stations):
        district = np.random.choice(districts)
        segment = np.random.choice(segments, p=[0.4, 0.3, 0.2, 0.1])
        
        # Add some variation based on period
        base_score = np.random.uniform(0.3, 0.9)
        trend_factor = period_offset * 0.02  # Slight improvement over time
        current_score = base_score + trend_factor + np.random.normal(0, 0.05)
        current_score = np.clip(current_score, 0.3, 0.95)
        
        last_year_score = current_score + np.random.normal(0, 0.1)
        last_year_score = np.clip(last_year_score, 0.3, 0.9)
        difference = current_score - last_year_score
        
        data.append({
            'ROC': 1000 + i,
            'İstasyon': station,
            'DISTRICT': district,
            'SKOR': current_score,
            'GEÇEN SENE SKOR': last_year_score,
            'Fark': difference,
            'Site Segment': segment,
            'TRANSACTION': np.random.randint(1000, 50000),
            'NOR HEDEF': np.random.uniform(0.6, 0.7),
            'Geçerli': np.random.randint(10, 500),
            'Dosya_Adı': file_name,
            'Yükleme_Tarihi': datetime.now() - timedelta(days=period_offset*30)
        })
    
    return pd.DataFrame(data)

def file_upload_section():
    """File upload and management section"""
    st.sidebar.markdown("## 📁 DOSYA YÖNETİMİ")
    
    # File upload
    uploaded_files = st.sidebar.file_uploader(
        "Excel dosyalarını yükleyin:",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="TLAG verilerini içeren Excel dosyalarını seçin"
    )
    
    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            if file_name not in st.session_state.uploaded_files:
                # Load data
                df = load_excel_data(uploaded_file, file_name)
                if df is not None:
                    st.session_state.uploaded_files[file_name] = df
                    st.sidebar.success(f"✅ {file_name} yüklendi!")
    
    # Add sample data for demo
    if st.sidebar.button("📊 Demo Verisi Ekle"):
        for i, period in enumerate(['Ocak 2024', 'Şubat 2024', 'Mart 2024']):
            sample_df = generate_sample_data(f"TLAG_{period}.xlsx", i)
            st.session_state.uploaded_files[f"TLAG_{period}.xlsx"] = sample_df
        st.sidebar.success("Demo verileri eklendi!")
    
    # Display uploaded files
    if st.session_state.uploaded_files:
        st.sidebar.markdown("### 📋 Yüklenen Dosyalar")
        
        file_names = list(st.session_state.uploaded_files.keys())
        selected_files = st.sidebar.multiselect(
            "Analiz için dosya seçin:",
            options=file_names,
            default=file_names[:2] if len(file_names) >= 2 else file_names,
            help="Karşılaştırma için en az 1, en fazla 3 dosya seçebilirsiniz"
        )
        
        st.session_state.selected_files = selected_files
        
        # Show file details
        for file_name in file_names:
            df = st.session_state.uploaded_files[file_name]
            with st.sidebar.expander(f"📄 {file_name}"):
                st.write(f"**İstasyon sayısı:** {len(df)}")
                st.write(f"**Ortalama skor:** {df['SKOR'].mean():.3f}")
                st.write(f"**Yükleme tarihi:** {df['Yükleme_Tarihi'].iloc[0].strftime('%d.%m.%Y %H:%M')}")
                
                if st.button(f"🗑️ Sil", key=f"delete_{file_name}"):
                    del st.session_state.uploaded_files[file_name]
                    if file_name in st.session_state.selected_files:
                        st.session_state.selected_files.remove(file_name)
                    st.rerun()

def compare_dataframes(dfs, file_names):
    """Compare multiple dataframes and return insights"""
    if len(dfs) < 2:
        return {}
    
    comparison = {}
    
    # Basic metrics comparison
    for i, (df, name) in enumerate(zip(dfs, file_names)):
        comparison[name] = {
            'total_stations': len(df),
            'avg_score': df['SKOR'].mean(),
            'top_performers': len(df[df['Site Segment'] == 'My Precious']),
            'improvement_count': len(df[df['Fark'] > 0]),
            'best_district': df.groupby('DISTRICT')['SKOR'].mean().idxmax(),
            'worst_segment': df.groupby('Site Segment')['SKOR'].mean().idxmin()
        }
    
    # Calculate changes between periods
    if len(dfs) == 2:
        df1, df2 = dfs[0], dfs[1]
        name1, name2 = file_names[0], file_names[1]
        
        # Merge on station for comparison
        merged = df1.merge(df2, on=['ROC', 'İstasyon'], suffixes=('_1', '_2'), how='inner')
        
        comparison['changes'] = {
            'score_change': (merged['SKOR_2'] - merged['SKOR_1']).mean(),
            'improved_stations': len(merged[merged['SKOR_2'] > merged['SKOR_1']]),
            'declined_stations': len(merged[merged['SKOR_2'] < merged['SKOR_1']]),
            'biggest_improver': merged.loc[merged['SKOR_2'] - merged['SKOR_1'].idxmax(), 'İstasyon_1'],
            'biggest_decliner': merged.loc[merged['SKOR_2'] - merged['SKOR_1'].idxmin(), 'İstasyon_1']
        }
    
    return comparison

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 TLAG MULTI-PERIOD ANALYSIS</h1>', 
                unsafe_allow_html=True)
    
    # File upload section
    file_upload_section()
    
    # Check if files are selected
    if not st.session_state.selected_files:
        st.info("👈 Lütfen sol panelden analiz edilecek dosyaları seçin.")
        
        # Show demo instructions
        st.markdown("## 🎯 Nasıl Kullanılır?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="file-card">
                <h3>1️⃣ Dosya Yükle</h3>
                <p>Sol panelden Excel dosyalarınızı yükleyin</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="file-card">
                <h3>2️⃣ Karşılaştır</h3>
                <p>2-3 dosya seçerek dönemsel analiz yapın</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="file-card">
                <h3>3️⃣ Analiz Et</h3>
                <p>Detaylı raporları ve trendleri görün</p>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Load selected dataframes
    selected_dfs = []
    for file_name in st.session_state.selected_files:
        selected_dfs.append(st.session_state.uploaded_files[file_name])
    
    # Combine all selected data
    combined_df = pd.concat(selected_dfs, ignore_index=True)
    
    # Performance comparison
    comparison = compare_dataframes(selected_dfs, st.session_state.selected_files)
    
    # Main metrics comparison
    st.markdown("## 📊 DÖNEMSEL KARŞILAŞTIRMA")
    
    cols = st.columns(len(st.session_state.selected_files))
    
    for i, file_name in enumerate(st.session_state.selected_files):
        with cols[i]:
            df = selected_dfs[i]
            avg_score = df['SKOR'].mean()
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>{file_name.replace('.xlsx', '').replace('TLAG_', '')}</h3>
                <h2>{len(df)}</h2>
                <p>İstasyon</p>
                <h2>{avg_score:.3f}</h2>
                <p>Ortalama Skor</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Trend Analysis
    if len(selected_dfs) >= 2:
        st.markdown("## 📈 TREND ANALİZİ")
        
        # Time series plot
        trend_data = []
        for file_name, df in zip(st.session_state.selected_files, selected_dfs):
            trend_data.append({
                'Dönem': file_name.replace('.xlsx', '').replace('TLAG_', ''),
                'Ortalama_Skor': df['SKOR'].mean(),
                'My_Precious_Sayısı': len(df[df['Site Segment'] == 'My Precious']),
                'Gelişen_İstasyon': len(df[df['Fark'] > 0])
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.line(trend_df, x='Dönem', y='Ortalama_Skor', 
                          title="Ortalama Skor Trendi",
                          markers=True)
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(trend_df, x='Dönem', y='My_Precious_Sayısı',
                         title="My Precious İstasyon Sayısı",
                         color='My_Precious_Sayısı',
                         color_continuous_scale='Greens')
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed comparison for 2 files
    if len(selected_dfs) == 2 and 'changes' in comparison:
        st.markdown("## 🔄 DETAY KARŞILAŞTIRMA")
        
        changes = comparison['changes']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score_change = changes['score_change']
            trend_class = "trend-positive" if score_change > 0 else "trend-negative"
            st.markdown(f"""
            <div class="comparison-card">
                <h3>Skor Değişimi</h3>
                <h2 class="{trend_class}">{score_change:+.3f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="comparison-card">
                <h3>Gelişen İstasyon</h3>
                <h2 class="trend-positive">{changes['improved_stations']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="comparison-card">
                <h3>Gerileyen İstasyon</h3>
                <h2 class="trend-negative">{changes['declined_stations']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            net_improvement = changes['improved_stations'] - changes['declined_stations']
            trend_class = "trend-positive" if net_improvement > 0 else "trend-negative"
            st.markdown(f"""
            <div class="comparison-card">
                <h3>Net Gelişim</h3>
                <h2 class="{trend_class}">{net_improvement:+d}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Station-level comparison chart
        df1, df2 = selected_dfs[0], selected_dfs[1]
        merged = df1.merge(df2, on=['ROC', 'İstasyon'], suffixes=('_Önceki', '_Sonraki'), how='inner')
        merged['Değişim'] = merged['SKOR_Sonraki'] - merged['SKOR_Önceki']
        
        fig3 = px.scatter(merged, x='SKOR_Önceki', y='SKOR_Sonraki',
                         color='Değişim', size='TRANSACTION_Sonraki',
                         hover_data=['İstasyon', 'DISTRICT_Sonraki'],
                         title="İstasyon Bazında Skor Karşılaştırması",
                         color_continuous_scale='RdYlGn')
        
        # Add diagonal line (no change)
        fig3.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                      line=dict(color="gray", width=2, dash="dash"))
        
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)
    
    # Segment Analysis Across Periods
    st.markdown("## 🎯 SEGMENT ANALİZİ")
    
    # Create segment comparison
    segment_data = []
    for file_name, df in zip(st.session_state.selected_files, selected_dfs):
        for segment in df['Site Segment'].unique():
            if pd.notna(segment):
                segment_df = df[df['Site Segment'] == segment]
                segment_data.append({
                    'Dönem': file_name.replace('.xlsx', '').replace('TLAG_', ''),
                    'Segment': segment,
                    'Sayı': len(segment_df),
                    'Ortalama_Skor': segment_df['SKOR'].mean()
                })
    
    segment_comparison_df = pd.DataFrame(segment_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig4 = px.bar(segment_comparison_df, x='Dönem', y='Sayı', 
                     color='Segment', title="Dönemsel Segment Dağılımı",
                     color_discrete_map={
                         'My Precious': '#2E8B57',
                         'Wasted Talent': '#DAA520', 
                         'Saboteur': '#DC143C',
                         'Primitive': '#708090'
                     })
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        fig5 = px.line(segment_comparison_df, x='Dönem', y='Ortalama_Skor', 
                      color='Segment', title="Segment Bazında Skor Trendi",
                      markers=True,
                      color_discrete_map={
                          'My Precious': '#2E8B57',
                          'Wasted Talent': '#DAA520', 
                          'Saboteur': '#DC143C',
                          'Primitive': '#708090'
                      })
        fig5.update_layout(height=400)
        st.plotly_chart(fig5, use_container_width=True)
    
    # Export functionality
    st.markdown("## 💾 RAPOR İNDİRME")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Combined data export
        csv = combined_df.to_csv(index=False)
        st.download_button(
            label="📄 Tüm Veriyi İndir",
            data=csv,
            file_name=f"tlag_combined_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Comparison summary
        if comparison:
            summary_data = []
            for file_name in st.session_state.selected_files:
                if file_name in comparison:
                    comp = comparison[file_name]
                    summary_data.append({
                        'Dosya': file_name,
                        'Toplam_İstasyon': comp['total_stations'],
                        'Ortalama_Skor': f"{comp['avg_score']:.3f}",
                        'My_Precious': comp['top_performers'],
                        'En_İyi_Bölge': comp['best_district']
                    })
            
            summary_df = pd.DataFrame(summary_data)
            summary_csv = summary_df.to_csv(index=False)
            
            st.download_button(
                label="📊 Karşılaştırma Raporu",
                data=summary_csv,
                file_name=f"tlag_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Trend data export
        if len(selected_dfs) >= 2:
            trend_csv = trend_df.to_csv(index=False)
            st.download_button(
                label="📈 Trend Analizi",
                data=trend_csv,
                file_name=f"tlag_trends_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()