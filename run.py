from flask import Flask, render_template, request, jsonify
import atexit
import cf_deployment_tracker
import os
from crawler import Crawler

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

crawler = None

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('PORT', 8080))

@app.route('/')
def home():
    return render_template('index.html')

def main():
    app.run(host='0.0.0.0', port=port, debug=False)

    # get a crawler instance
    crawler = Crawler()

    # import the api to use
    from crawler.crawlerhelpers import efa_beta

    #import the db to use
    from crawler.crawlerhelpers import cloudant_db

    # register api
    crawler.add_api( efa_beta.get_name(), efa_beta.get_base_url(), get_params_function=efa_beta.get_params, function_to_call=efa_beta.function_to_call)
    crawler.set_db_session(cloudant_db.get_db_session('vcap-local.json'), 'vvs-delay-db')

    # run apis with the following station ids
    station_ids = ['6008']
    crawler.run(station_ids)

@atexit.register
def shutdown():
    if crawler:
        crawler.close_db_session()

if __name__ == '__main__':
    main()
