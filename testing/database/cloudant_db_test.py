from crawler.crawlerhelpers import cloudant_db

def test():
    failed = False
    
    try:
        client = cloudant_db.get_db_session('vcap-local.json')
        print "Loading credentials \t - check"
    except:
        failed = True
        print "Loading credentials \t - fail"

    try:
        db = client.create_database('test')
    except:
        client.delete_database('test')
        db = client.create_database('test')
    if db.exists():
        print "DB Connection \t\t - check"
    else:
        failed = True
        print "DB Connection \t\t - fail"

    doc = db.create_document({
        '_id': '1',
        'name': 'Julia',
        'age': 30,
        'pets': ['cat', 'dog', 'frog']
    })
    if doc.exists():
        print "Document creation \t - check"
    else:
        failed = True
        print "Document creation \t - fail"

    db.create_document({
        '_id': '2',
        'name': 'Hannah',
        'age': 20,
        'pets': ['cat', 'mouse']
    })
    db.create_document({
        '_id': '3',
        'name': 'Steffi',
        'age': 77,
        'children': ['Tom', 'Peter']
    })

    hannah = db['2']
    if hannah.exists():
        print "Document retrieval \t - check"
    else:
        failed = True
        print "Document retrieval \t - fail"

    hannah.update_field(hannah.field_set, 'age', 21)
    hannah.update_field(hannah.list_field_append, 'pets', 'wombat')
    hannah.fetch()
    if (hannah['age'] == 21) & ('wombat' in hannah['pets']):
        print "Document update \t - check"
    else:
        failed = True
        print "Document update \t - fail"

    hannah.delete()
    if db.doc_count() == 2:
        print "Document deletion \t - check"
    else:
        failed = True
        print "Document update \t - fail"

    try:
        db.create_document({
            '_id': '3',
            'name': 'Ursel',
            'age': 12,
        })
        failed = True
        print "Throw Key Error \t - fail"
    except:
        print "Throw Key Error \t - check"

    client.disconnect()
    print "Disconnected from DB"

    return failed


if __name__ == '__main__':
    test()
