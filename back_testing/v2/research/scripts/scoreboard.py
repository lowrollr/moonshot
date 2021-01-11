
import dominate
import hjson




def updateScoreboard(model_name, model_version, score, trades, features):
    scores = dict()
    with open('scores.hjson') as scores:
        scores = hjson.load(scores)


    new_score_items = scores[(model_name, model_version)] = dict()
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
                for name, version in scores.keys():
                    row = tr()
                    row.add(td(f'{name} v.{version}'))
                    row.add(td(scores[(name, version)]['score']))
                    row.add(td(scores[(name, version)]['trades']))

    with open('./v2/research/scripts/scoreboard.html', 'w') as output:
        output.write(str(doc))

        
