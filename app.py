"""English guided interface for the historical Ibirapuera LiDAR audit."""
import json
import os
import base64
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from pyproj import Transformer
from audit import ROOT, LABELS, ROI

COLORS={2:'#d7af72',5:'#74d16c',6:'#e67b35',9:'#239bc0',19:'#a78bca',20:'#8897a9'}
NAMES={2:'Ground',5:'Tall vegetation',6:'Built structures',9:'Water',19:'Unresolved code 19',20:'Unresolved code 20'}
st.set_page_config(page_title='Ibirapuera LiDAR Lab',page_icon='🌳',layout='wide')
with st.sidebar:
    st.markdown('### Park atmosphere')
    wallpaper=st.selectbox('Wallpaper',['Ibirapuera trees','Ibirapuera lake','Solid forest green'])
    st.caption('Real park photographs, stored locally. Decorative views, not live images or a photo of the exact LiDAR crop.')
    if wallpaper=='Ibirapuera trees':
        st.caption('Photo: Daderot · 17 October 2015 · CC0 · Wikimedia Commons')
    elif wallpaper=='Ibirapuera lake':
        st.caption('Photo: Wilfredor · 21 September 2014 · CC0 · Wikimedia Commons')
photo={'Ibirapuera trees':'trees.jpg','Ibirapuera lake':'lake.jpg'}.get(wallpaper)
background='none'
if photo:
    encoded=base64.b64encode((ROOT/'assets'/photo).read_bytes()).decode('ascii')
    background=f'linear-gradient(rgba(4,26,17,.40),rgba(4,26,17,.67)),url("data:image/jpeg;base64,{encoded}")'
st.markdown("""<style>
.stApp {background-color:#09291c;background-image:BACKGROUND_IMAGE;background-size:cover;background-position:center;background-attachment:fixed}
[data-testid="stHeader"]{background:rgba(6,29,19,.88)}
.block-container{padding:1.5rem 2rem 2rem;max-width:1500px;background:rgba(7,31,21,.86);border:1px solid rgba(174,224,171,.25);border-radius:20px;margin-top:1rem;box-shadow:0 12px 48px #00180c66}
h1,h2,h3{color:#d2f2b4!important}
[data-testid="stMetric"]{background:rgba(32,72,46,.94);border:1px solid #527c56;border-radius:12px;padding:12px}
[data-testid="stAlert"] p{color:#e2f4ff!important}
[data-testid="stMetricValue"]{color:#edffd8}
[data-testid="stCaptionContainer"]{color:#c8dcc9}
[data-testid="stSidebar"]{background:rgba(8,36,24,.97);border-right:1px solid #40694b}
[data-testid="stExpander"]{background:rgba(20,53,35,.95);border-radius:10px}
[data-testid="stPlotlyChart"]{border:1px solid #41634a;border-radius:14px;overflow:hidden;background:#102e20}
a{color:#b8e79e}
@media(max-width:700px){.block-container{padding:1rem;margin-top:0;border-radius:0}}
</style>""".replace('BACKGROUND_IMAGE',background),unsafe_allow_html=True)
SCREENS = {
    'V1': ('Data Audit', ['3D Explorer', 'Study Location', 'Data Coverage', 'Sources & Limits']),
    'V2': ('Point Cloud Explorer', ['3D Explorer']),
    'V3': ('Terrain & Surface Models', ['V3 Models']),
    'V4': ('Heights & Profiles', ['V4 Heights & Profiles']),
    'V5': ('Historical Imagery', ['V5 Historical Imagery']),
    'V6': ('Reproducibility', ['V6 Reproducibility']),
}
version = os.environ.get('IBIRAPUERA_SCREEN')
if version not in SCREENS:
    selected_screen = st.sidebar.selectbox(
        'Project version',
        ['Integrated Learning Lab', *SCREENS],
        format_func=lambda screen: (
            f'{screen} · {SCREENS[screen][0]}' if screen in SCREENS else screen
        ),
    )
    version = selected_screen if selected_screen in SCREENS else None
title = f'{version} · {SCREENS[version][0]}' if version else 'V6 · Integrated Learning Lab'
st.title('Ibirapuera LiDAR Lab')
st.header(title)
st.caption('Forest Edition · Ibirapuera Park · São Paulo, Brazil · by Raquel Cruz')
st.write('Explore a real laser survey: each dot is a measured position on the ground, vegetation or a structure.')
st.info('Historical survey: 2017 collection. These views do not show current park conditions.')
if not (ROOT/'outputs/audit.json').exists():
    st.error('The audit results are missing. In the PyCharm terminal, run: python audit.py --download')
    st.stop()
report=json.loads((ROOT/'outputs/audit.json').read_text(encoding='utf-8'))
with np.load(ROOT/'outputs/preview.npz') as data:
    points,coverage,ground=data['points'],data['coverage'],data['ground']
    rgb = data['rgb'] if 'rgb' in data.files else None
has_rgb = rgb is not None and rgb.shape == (len(points), 3)
a,b,c=st.columns(3)
a.metric('Area being studied','200 × 200 m',help='Four hectares: a small portion of the park, not the entire Ibirapuera.')
b.metric('Measured points in this area',f"{report['roi']['point_count']:,}",help='Total counted from the original LAZ, including every source class.')
c.metric('Average points per square metre',f"{report['roi']['density_all_returns_per_m2']:.2f}",help='All recorded returns divided by area. This is not an accuracy or image-resolution claim.')
pages = SCREENS[version][1] if version else [
    '3D Explorer', 'Study Location', 'Data Coverage', 'V3 Models', 'V4 Heights & Profiles',
    'V5 Historical Imagery', 'V6 Reproducibility', 'Sources & Limits', 'Version Roadmap',
]
page = (st.radio('Explore the study', pages, horizontal=True, label_visibility='collapsed')
        if len(pages) > 1 else pages[0])
if page=='3D Explorer':
    st.subheader('See how measured points reveal the landscape')
    controls,canvas=st.columns([1,3])
    with controls:
        presets = ['Ground + vegetation + structures', 'Ground only',
                   'Ground + vegetation', 'Built structures only', 'All source classes']
        if version != 'V1':
            presets.append('Custom classes')
        preset = st.selectbox('What would you like to see?', presets)
        choices={'Ground + vegetation + structures':[2,5,6],'Ground only':[2],'Ground + vegetation':[2,5],'Built structures only':[6],'All source classes':sorted(np.unique(points[:,3]).astype(int).tolist())}
        if preset == 'Custom classes':
            selected = st.multiselect('Source classes', choices['All source classes'],
                                      default=[code for code in (2,5,6) if code in choices['All source classes']],
                                      format_func=lambda code: f"{code} · {NAMES.get(code, 'Other')}")
        else:
            selected = choices[preset]
        modes = ['Landscape group', 'Source elevation']
        if version != 'V1' and has_rgb:
            modes.append('Source RGB')
        elif version != 'V1':
            st.caption('Run python audit.py to rebuild the preview with available source RGB.')
        color=st.radio('Colour by',modes)
        if version != 'V1':
            st.caption('Source RGB displays the colours stored in the historical LAZ.')
        camera=st.selectbox('Viewpoint',['Angled view','Top view','Side view'])
        cap=st.select_slider('Display detail',options=[10000,30000,60000,100000],value=30000,format_func=lambda n:f'{n:,} points')
        size=st.slider('Dot size',1.0,4.0,2.0,step=0.5)
        st.caption('Drag to rotate · Scroll to zoom · Use the plot toolbar to reset or save a PNG.')
        st.write('**Landscape groups**')
        for cls in selected:
            st.markdown(f'<span style="color:{COLORS.get(cls,"#999")}">●</span> {NAMES.get(cls,str(cls))}',unsafe_allow_html=True)
        st.caption('Group labels come from the source classification. They are not field-verified.')
    with canvas:
        indices = np.flatnonzero(np.isin(points[:, 3], selected))[:cap]
        p = points[indices]
        fig=go.Figure()
        eyes={'Angled view':dict(x=1.35,y=-1.6,z=1.0),'Top view':dict(x=0,y=0,z=2.5),'Side view':dict(x=0,y=-2.5,z=0.15)}
        if not len(p):
            st.info('Select at least one source class to display points.')
        if color == 'Source RGB' and len(p):
            colours = np.rint(rgb[indices] / 257).astype(np.uint8)
            markers = [f'rgb({red},{green},{blue})' for red, green, blue in colours]
            fig.add_trace(go.Scatter3d(x=p[:,0]-ROI[0], y=p[:,1]-ROI[1], z=p[:,2],
                                       mode='markers', marker=dict(size=size,color=markers)))
        elif color=='Source elevation':
            fig.add_trace(go.Scatter3d(x=p[:,0]-ROI[0],y=p[:,1]-ROI[1],z=p[:,2],mode='markers',marker=dict(size=size,color=p[:,2],colorscale='Viridis',colorbar=dict(title='Source Z (m)')),hovertemplate='East: %{x:.2f} m<br>North: %{y:.2f} m<br>Source Z: %{z:.2f} m<extra></extra>'))
        else:
            for cls in selected:
                q=p[p[:,3]==cls]
                fig.add_trace(go.Scatter3d(x=q[:,0]-ROI[0],y=q[:,1]-ROI[1],z=q[:,2],mode='markers',name=NAMES.get(cls,str(cls)),marker=dict(size=size,color=COLORS.get(cls,'#999')),hovertemplate='East: %{x:.2f} m<br>North: %{y:.2f} m<br>Source Z: %{z:.2f} m<extra>%{fullData.name}</extra>'))
        fig.update_layout(font=dict(color='#e0eee2'),height=650,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,paper_bgcolor='#102e20',scene=dict(bgcolor='#102e20',xaxis=dict(backgroundcolor='#163926',gridcolor='#40644a'),yaxis=dict(backgroundcolor='#163926',gridcolor='#40644a'),zaxis=dict(backgroundcolor='#163926',gridcolor='#40644a'),aspectmode='data',camera=dict(eye=eyes[camera]),xaxis_title='East within study (m)',yaxis_title='North within study (m)',zaxis_title='Source Z (m)'),uirevision=f'{camera}-{color}')
        if len(p):
            st.plotly_chart(fig,width='stretch',config={'displaylogo':False,'scrollZoom':True,
                            'toImageButtonOptions': {'filename':'ibirapuera_v2_view','format':'png'}})
            if version != 'V1' and st.checkbox('Prepare interactive HTML export'):
                export = fig.to_html(include_plotlyjs=True, config={'displaylogo':False})
                st.download_button('Download interactive view', export,
                                   file_name='ibirapuera_v2_view.html', mime='text/html')
            if version != 'V1':
                st.caption('HTML captures the selected classes, colours and viewpoint preset. The plot toolbar saves a PNG of the current camera view.')
        st.caption(f'Showing {len(p):,} sampled points · Full study-area count: {report["roi"]["point_count"]:,} · Natural spatial proportions, no vertical exaggeration.')
    st.warning('Source Z is an elevation coordinate, not tree height. The vertical reference is unresolved. Codes 19/20 are hidden in the default view but remain included in the audit.')
    with st.expander('Try this two-minute learning exercise'):
        st.markdown('1. Select **Ground only** to see source points labelled as soil.\n2. Select **Ground + vegetation** to reveal the points above it.\n3. Select **Top view** to examine their distribution.\n4. Select **All source classes** to see the unresolved groups too.\n\nAn apparent gap in a sample does not establish a gap in the full survey. Use Data Coverage to inspect full counts.')
elif page=='Study Location':
    st.subheader('Where is this 4-hectare study area?')
    st.write('The green square marks the study area within Ibirapuera Park. The broader map provides context; only the square is audited.')
    transform=Transformer.from_crs(31983,4326,always_xy=True)
    x=[ROI[0],ROI[2],ROI[2],ROI[0],ROI[0]];y=[ROI[1],ROI[1],ROI[3],ROI[3],ROI[1]]
    lon,lat=transform.transform(x,y); center=transform.transform((ROI[0]+ROI[2])/2,(ROI[1]+ROI[3])/2)
    fig=go.Figure(go.Scattermap(lon=lon,lat=lat,mode='lines',fill='toself',line=dict(color='#16864a',width=4),name='Audited study area',hovertemplate='Study boundary · 200 × 200 m<extra></extra>'))
    fig.update_layout(map=dict(style='open-street-map',center=dict(lon=center[0],lat=center[1]),zoom=14),height=570,margin=dict(l=0,r=0,t=0,b=0),showlegend=False)
    st.plotly_chart(fig,width='stretch')
    st.caption('Basemap © OpenStreetMap contributors. Map tiles need internet; the 3D viewer and audit work locally. Basemap and LiDAR have different dates.')
    st.link_button('Open location in OpenStreetMap',f'https://www.openstreetmap.org/?mlat={center[1]:6f}&mlon={center[0]:6f}#map=16/{center[1]:6f}/{center[0]:6f}')
    st.write(f'Centre: latitude {center[1]:.6f}, longitude {center[0]:.6f}. Working CRS: EPSG:31983, assigned from the external tile index.')
    with st.expander('Coordinate bounds (available offline)'):
        st.json(dict(west_easting=ROI[0],south_northing=ROI[1],east_easting=ROI[2],north_northing=ROI[3],units='metres',crs='EPSG:31983'))
elif page=='Data Coverage':
    st.subheader('Where do we have measured points?')
    st.write('Each square represents 5 × 5 metres. Colour shows the number of points, not height. These counts use the complete study-area input, not the 3D sample.')
    layer=st.radio('Inspect',['All measured points','Ground points only'],horizontal=True)
    grid=coverage if layer=='All measured points' else ground
    a,b=st.columns(2); a.metric('Cells containing points',f'{np.count_nonzero(grid):,} / {grid.size:,}');b.metric('Cells without these points',f'{np.count_nonzero(grid==0):,}')
    fig=go.Figure(go.Heatmap(z=grid,x=np.arange(2.5,200,5),y=np.arange(2.5,200,5),colorscale='YlGnBu',colorbar_title='Points / 25 m²',hovertemplate='East: %{x} m<br>North: %{y} m<br>Points: %{z}<extra></extra>'))
    fig.update_layout(paper_bgcolor='#102e20',plot_bgcolor='#102e20',font=dict(color='#e0eee2'),height=550,xaxis_title='East within study (m)',yaxis_title='North within study (m)',yaxis=dict(scaleanchor='x'),margin=dict(t=15))
    st.plotly_chart(fig,width='stretch')
    st.info('A cell with points is not proof of complete coverage. Explore V3 Models to see where ground measurements support the terrain grid.')
elif page in ('V3 Models', 'V4 Heights & Profiles'):
    from model_views import show_models
    show_models(height_page=page=='V4 Heights & Profiles')
elif page=='V5 Historical Imagery':
    from imagery import LAYERS, fetch_image, image_url
    st.subheader('V5 · Compare GeoSampa imagery')
    st.write('The two images use the same 200 × 200 m extent and EPSG:31983. Differences may reflect lighting, acquisition conditions, alignment or actual change. This is a visual comparison.')
    st.caption('Year labels come from GeoSampa layer names. Images are fetched from the municipal service when requested.')
    if st.button('Load 2017 and 2020 imagery'):
        results = {}
        for year in LAYERS:
            try:
                results[year] = fetch_image(year)
            except (OSError, ValueError) as error:
                results[year] = str(error)
        st.session_state['historical_images'] = results
    for column, year in zip(st.columns(2), LAYERS):
        with column:
            st.markdown(f'**GeoSampa · {year}**')
            result = st.session_state.get('historical_images', {}).get(year)
            if isinstance(result, bytes):
                st.image(result, width='stretch')
            elif result:
                st.warning(f'Image unavailable. {result}')
            st.link_button(f'Open {year} image at GeoSampa', image_url(year))
elif page=='V6 Reproducibility':
    from release import MANIFEST, verify
    st.subheader('V6 · Reproduce the study')
    st.write('The release includes the original LAZ, audited preview and calculated model grids.')
    st.code('python audit.py\npython models.py\npython release.py --record', language='powershell')
    st.caption('Record a new manifest after a deliberate rebuild. Use python release.py to verify the delivered files.')
    if st.button('Verify packaged data'):
        results = verify()
        st.table([{'File':name,'Integrity':'OK' if ok else 'Mismatch'} for name,ok in results.items()])
    st.download_button('Download SHA-256 manifest', MANIFEST.read_bytes(),
                       'release_manifest.json', mime='application/json')
elif page=='Sources & Limits':
    st.subheader('Real measurements, documented boundaries')
    st.write('Provider: São Paulo City Hall / GeoSampa. Collection: 2017. Exact flight date of this tile remains unverified.')
    st.dataframe([{'Source code':int(k),'Meaning':NAMES.get(int(k),'Other'),'All points in study':v} for k,v in report['roi_classes'].items()],hide_index=True)
    for line in report['limitations']:st.write('• '+line)
    st.warning('The AWS LAZ has no embedded CRS. EPSG:31983 is assigned from an external index. The source Z vertical reference and codes 19/20 remain unresolved.')
    st.markdown('[Dataset registry](https://registry.opendata.aws/pmsp-lidar/) · [OpenTopography collection and tile index](https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.062020.31983.1)')
    st.caption('Dataset licence declared by its registry: GNU GPL v3.0. Orthophotos are not bundled. No current survey, live camera or live satellite feed is included.')
    st.download_button('Download full audit report',json.dumps(report,indent=2),file_name='ibirapuera_audit.json',mime='application/json')
    with st.expander('Technical audit details'):st.json(report)
else:
    st.subheader('Six major versions, with focused intermediate revisions')
    st.table([{'Version':'V1 / V1.1','Delivery':'Data audit + guided interface','Status':'Implemented'}, {'Version':'V2','Delivery':'Expanded point-cloud exploration, RGB and exports','Status':'Implemented'}, {'Version':'V3','Delivery':'Terrain and surface models with support masks','Status':'Implemented with support masks'}, {'Version':'V4','Delivery':'Height above ground and profiles','Status':'Implemented where both models are supported'}, {'Version':'V5','Delivery':'Historical imagery comparison','Status':'On-demand GeoSampa comparison'}, {'Version':'V6','Delivery':'Reproducible final educational release','Status':'Implemented'}])
    st.caption('Intermediate revisions do not add a major version. Live Park View has been removed from scope. All releases remain educational and historical.')
