"""Streamlit views for the V3 and V4 study grids."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from models import CENTRES, MODEL, MIN_POINTS, grid_csv

TITLES = {'terrain': 'Terrain · median ground Z',
          'surface': 'Surface · highest return Z',
          'height': 'Surface above terrain'}


def show_models(height_page=False):
    if not MODEL.exists():
        st.error('Model grids are missing. Run python models.py in the project terminal.')
        return
    with np.load(MODEL) as archive:
        grids = {name: archive[name] for name in archive.files}
    if height_page:
        st.subheader('V4 · Height above terrain and cross-sections')
        st.write('Each valid cell shows the difference between its highest return and median ground elevation. The result describes a cell, not an individual tree or structure.')
        model = 'height'
    else:
        st.subheader('V3 · Terrain and surface models')
        st.write(f'Each 5 × 5 m cell needs at least {MIN_POINTS} eligible returns. Terrain uses ground class 2. Surface uses the highest eligible return from any source class. Withheld points are excluded.')
        model = st.radio('Model', ['terrain', 'surface'], format_func=TITLES.get, horizontal=True)
    values = grids[model]
    valid = np.isfinite(values)
    first, second = st.columns(2)
    first.metric('Supported cells', f'{valid.sum():,} / {valid.size:,}')
    second.metric('Cells with gaps', f'{(~valid).sum():,}')
    mode = st.radio('View', ['Elevation grid', '3D model', 'Support mask'], horizontal=True,
                    index=0)
    if mode == '3D model':
        fig = go.Figure(go.Surface(x=CENTRES, y=CENTRES, z=values,
                                   connectgaps=False, colorscale='Viridis',
                                   colorbar_title='m'))
        fig.update_layout(scene=dict(xaxis_title='East offset (m)',
                                     yaxis_title='North offset (m)',
                                     zaxis_title='Metres', aspectmode='data'))
    else:
        support = mode == 'Support mask'
        z = valid.astype(int) if support else values
        fig = go.Figure(go.Heatmap(
            x=CENTRES, y=CENTRES, z=z,
            customdata=np.dstack((grids['counts'], grids['ground_counts'])),
            hovertemplate='East: %{x} m<br>North: %{y} m<br>Value: %{z}<br>All returns: %{customdata[0]}<br>Ground returns: %{customdata[1]}<extra></extra>',
            colorscale=[[0, '#a75c60'], [1, '#80c78c']] if support else 'Viridis',
            colorbar=dict(tickvals=[0, 1], ticktext=['Gap', 'Supported']) if support else dict(title='m'),
            hoverongaps=False))
        fig.update_layout(xaxis_title='East offset (m)', yaxis_title='North offset (m)',
                          yaxis=dict(scaleanchor='x'), plot_bgcolor='#552f36')
    fig.update_layout(height=560, paper_bgcolor='#102e20', font_color='#e0eee2',
                      margin=dict(t=20, b=45, l=50, r=20))
    st.plotly_chart(fig, width='stretch')
    st.caption('Gaps are left blank in the elevation grid and 3D model. The support mask marks them in red. The vertical datum of source Z remains unresolved.')
    if height_page:
        row = st.select_slider('East–west profile · north offset (m)',
                               options=CENTRES.tolist(), value=102.5)
        index = int(row // 5)
        profile = go.Figure()
        for key in ('terrain', 'surface'):
            profile.add_scatter(x=CENTRES, y=grids[key][index], name=TITLES[key],
                                mode='lines+markers', connectgaps=False)
        profile.update_layout(xaxis_title='East offset (m)', yaxis_title='Source Z (m)',
                              paper_bgcolor='#102e20', font_color='#e0eee2')
        st.plotly_chart(profile, width='stretch')
    st.download_button('Download model grid CSV', grid_csv(grids), 'ibirapuera_models.csv',
                       mime='text/csv')
