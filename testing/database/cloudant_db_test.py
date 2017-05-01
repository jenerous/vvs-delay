from crawler.crawlerhelpers import cloudant_db
from config import settings

def test():
    failed = False
    db = None

    try:
        db = cloudant_db.CloudantDB(settings.CLOUDANT_CRED_FILE, 'test')
        print "Creating DB instance \t - check"
    except:
        failed = True
        print "Creating DB instance \t - fail"

    #purge old data
    doc1 = db.db['item1']
    doc2 = db.db['item2']
    if doc1.exists():
        doc1.delete()
    if doc2.exists():
        doc2.delete()

    try:
        data = []
        data.append({
            '_id': 'item1',
            'name': 'Julia',
            'age': 30,
            'pets': ['cat', 'dog', 'frog']
        })
        data.append({
            '_id': 'item2',
            'name': 'Test',
            'age': 20,
            'pets': ['test']
        })
        db.write_to_db(data)

        doc1 = db.db['item1']
        doc2 = db.db['item2']
        if doc1.exists() & doc2.exists():
            print "Writing to DB \t\t - check"
        else:
            print "Writing to DB \t\t - fail"
    except:
        failed = True
        print "Writing to DB \t\t - fail (Exception!)"

    db.close_session()

    return failed


if __name__ == '__main__':
    test()
