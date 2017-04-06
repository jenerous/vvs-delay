from crawler import Crawler

def main():

    # get a crawler instance
    crawler = Crawler()

    # import the api to use
    from crawler.crawlerhelpers import efa_beta

    # register api
    crawler.add_api( efa_beta.get_name(), efa_beta.get_base_url(), get_params_function=efa_beta.get_params, function_to_call=efa_beta.function_to_call)

    # run apis with the following station ids
    station_ids = ['6008']
    crawler.run(station_ids)

if __name__ == '__main__':
    main()
