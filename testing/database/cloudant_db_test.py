from crawler.crawlerhelpers import cloudant_db
from config import settings
from time import sleep


def test():
    counter = 0
    failed = False
    db = None
    try:
        db = cloudant_db.CloudantDB(settings.CLOUDANT_CRED_FILE, 'test')
        print "Creating DB instance \t - check"
    except Exception:
        failed = True
        print "Creating DB instance \t - fail"
    # purge old data
    try:
        doc1 = db.db['item1']
    except Exception:
        doc1 = None

    try:
        doc2 = db.db['item2']
    except Exception:
        doc2 = None

    if doc1 is not None and doc1.exists():
        doc1.delete()
    if doc2 is not None and doc2.exists():
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
        sleep(1)
        doc1 = db.db['item1']
        doc2 = db.db['item2']
        if doc1.exists() & doc2.exists():
            print "Writing to DB \t\t - check"
        else:
            print "Writing to DB \t\t - fail"
            failed = True
    except Exception as e:
        failed = True
        print "Writing to DB \t\t - fail (Exception!)"
        print e

    db.close_session()
    # db.db_writer.close()
    # db.db_writer.join()

    return failed


if __name__ == '__main__':
    test()
