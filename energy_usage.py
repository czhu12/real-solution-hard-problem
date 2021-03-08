import plotly.graph_objects as go
import urllib, json
import pandas as pd
import urllib.request
import random
import plac
import os
# 105 aint bad
random.seed(107)

COLOR_CODES = {
  'Petroleum': 'rgba(39, 60, 117,0.8)',
  'Natural Gas': 'rgba(142, 68, 173,0.8)',
  'Coal': 'rgba(44, 62, 80,0.8)',

  'Nuclear': 'rgba(52, 152, 219,0.8)',
  'Solar': 'rgba(39, 174, 96,0.8)',
  'Wind': 'rgba(39, 174, 96,0.8)',
  'Hydro': 'rgba(39, 174, 96,0.8)',
  'Biomass & Other Renewables': 'rgba(39, 174, 96,0.8)',

  'Total Electricity': 'rgba(243, 156, 18,0.8)',
  'Used Electricity': 'rgba(230, 126, 34,0.8)',
  'Wasted Electricity': 'rgba(192, 57, 43,0.8)',

  'Residential': 'rgba(26, 188, 156,0.8)',
  'Industrial': 'rgba(149, 165, 166,0.8)',
  'Transportation': 'rgba(155, 89, 182,0.8)',
  'Commercial': 'rgba(211, 84, 0,0.8)',
}

@plac.pos('input_dir', "Input directory", type=str)
def main(input_dir):
    datafile = os.path.join(input_dir, 'data.csv')
    with open(os.path.join(input_dir, 'initial_conditions.json')) as f:
        sources_size = json.loads(f.read())

    df = pd.read_csv(datafile, sep=',').set_index('Source')
    consumers = df.keys()
    producers = df[consumers[0]].keys()
    print(df)
    id2label = sorted(list(set(list(consumers) + list(producers))))
    label2id = { l: i for i, l in enumerate(id2label) }

    
    # Iterate over df one index at a time
    sources = []
    targets = []
    values = []
    
    for target in df.keys():
        for source in df[target].keys():
            value = df[target][source]
            if value > 0:
                sources.append(label2id[source])
                targets.append(label2id[target])
                if source in sources_size:
                    value = value * sources_size[source] / 100.
                if target not in sources_size:
                    sources_size[target] = 0
                sources_size[target] += value
                values.append(value)
    
    id2label_with_percentages = ["{} {:.1f}%".format(label, sources_size[label]) for label in id2label]
    data = {
            "data": [
                {
                    "type": "sankey",
                    "domain": {
                        "x": [
                            0,
                            1
                        ],
                        "y": [
                            0,
                            1
                        ]
                    },
                    "orientation": "h",
                    "valueformat": ".0f",
                    "valuesuffix": "TWh",
                    "node": {
                        "pad": 15,
                        "thickness": 15,
                        "line": {
                            "color": "black",
                            "width": 0.5
                        },
                        "label": id2label_with_percentages,
                        "color": [COLOR_CODES[label] for label in id2label]
                    },
                    "link": {
                        "source": sources,
                        "target": targets,
                        "value": values,
                        "color": ["rgba(0,0,57,0.2)"] * len(sources),
                        "label": [''] * len(sources)
                    }
                }
            ],
            "layout": {
                "title": {"text": "My Chart"},
                "width": 1118,
                "height": 772,
                "font": {
                    "size": 10
                },
                "updatemenus": [
                    {
                        "y": 1,
                        "buttons": [
                            {
                                "label": "Light",
                                "method": "relayout",
                                "args": [ "paper_bgcolor", "white" ]
                            },
                            {
                                "label": "Dark",
                                "method": "relayout",
                                "args": [ "paper_bgcolor", "black"]
                            }
                        ]
                    },
                    {
                        "y": 0.9,
                        "buttons": [
                            {
                                "label": "Thick",
                                "method": "restyle",
                                "args": [ "node.thickness", 15 ]
                            },
                            {
                                "label": "Thin",
                                "method": "restyle",
                                "args": [ "node.thickness", 8]
                            }
                        ]
                    },
                    {
                        "y": 0.8,
                        "buttons": [
                            {
                                "label": "Small gap",
                                "method": "restyle",
                                "args": [ "node.pad", 15 ]
                            },
                            {
                                "label": "Large gap",
                                "method": "restyle",
                                "args": [ "node.pad", 20]
                            }
                        ]
                    },
                    {
                        "y": 0.7,
                        "buttons": [
                            {
                                "label": "Snap",
                                "method": "restyle",
                                "args": [ "arrangement", "snap" ]
                            },
                            {
                                "label": "Perpendicular",
                                "method": "restyle",
                                "args": [ "arrangement", "perpendicular"]
                            },
                            {
                                "label": "Freeform",
                                "method": "restyle",
                                "args": [ "arrangement", "freeform"]
                            },
                            {
                                "label": "Fixed",
                                "method": "restyle",
                                "args": [ "arrangement", "fixed"]
                            }
                        ]
                    },
                    {
                        "y": 0.6,
                        "buttons": [
                            {
                                "label": "Horizontal",
                                "method": "restyle",
                                "args": [ "orientation", "h" ]
                            },
                            {
                                "label": "Vertical",
                                "method": "restyle",
                                "args": [ "orientation", "v"]
                            }
                        ]
                    }
                ]
        }
    }
    
    opacity = 0.7
    data['data'][0]['node']['color'] = [color for color in data['data'][0]['node']['color']]
    data['data'][0]['link']['color'] = [data['data'][0]['node']['color'][src].replace("0.8", str(opacity))
                                        for src in data['data'][0]['link']['source']]
    
    fig = go.Figure(data=[go.Sankey(
        valueformat = ".0f",
        valuesuffix = "%",
        # Define nodes
        node = dict(
          pad = 15,
          thickness = 15,
          line = dict(color = "black", width = 0.5),
          label =  data['data'][0]['node']['label'],
          color =  data['data'][0]['node']['color']
        ),
        # Add links
        link = dict(
          source =  data['data'][0]['link']['source'],
          target =  data['data'][0]['link']['target'],
          value =  data['data'][0]['link']['value'],
          label =  data['data'][0]['link']['label'],
          color =  data['data'][0]['link']['color']
    ))])
    
    fig.update_layout(title_text="US Energy Consumption by Source and Sector, 2019 via Energy Information Administration", font_size=20)
    fig.show()
if __name__ == '__main__':
    plac.call(main)

