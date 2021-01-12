import dominate
from dominate.tags import *
from dominate.util import raw
import hjson




def updateScoreboard(model_name, model_version, score, trades, features):
    score_dict = dict()
    with open('./v2/research/scripts/scores.hjson', 'r') as scores:
        score_dict = hjson.load(scores)


    new_score_items = score_dict[f'{model_name}_v{model_version}'] = dict()
    new_score_items['score'] = score
    new_score_items['trades'] = trades
    new_score_items['features'] = features

    


    doc = dominate.document(title='Benchmark Scoreboard')

    with doc.head:
        link(rel='stylesheet', href='style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')

    with doc:
        with div():
            h1('Benchmark Scoreboard')
            with table().add(tbody()):
                for model in list(dict(sorted(score_dict.items(), key=lambda item:item[1]['score']))):
                    name, version = model.split('_v')
                    row = tr()
                    row.add(td(f'{name} v.{version}'))
                    row.add(td(score_dict[model]['score']))
                    row.add(td(score_dict[model]['trades']))

    with open('./v2/research/scripts/scoreboard.html', 'w') as output:
        output.write(str(doc))

    with open('./v2/research/scripts/scores.hjson', 'w') as scores:
        scores.write(hjson.dumps(score_dict))