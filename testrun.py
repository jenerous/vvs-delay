import os
import importlib

tests = []

for root, dirs, files in os.walk("testing"):
    for file in files:
        if file.endswith(".py") and not os.path.basename(file) == '__init__.py':
            # print 'found test', os.path.join(root, file)
            tests.append(os.path.join(root, file))

passed_or_failed = []
current_task = ''
for i, t in enumerate(tests):
    try:
        print '\n{}\n{:=^80}\n{}\n'.format('=' * 80, ' ' + t + ' ', '=' * 80)

        current_task = 'importing {}'.format(t)
        print '{}\n{}'.format('-' * 80, current_task)
        t_path = t.replace('/', '.')[:-3]
        current_test = importlib.import_module(t_path)
        print '## passed'
        current_task = 'running tests'
        print '{}\n{}\n##'.format('-' * 80, current_task)
        failed = current_test.test()

        passed_or_failed.append(True and not failed)
    except Exception as e:
        print 'FAILED'
        passed_or_failed.append(False)
        print 'EXCEPTION:', e

print '\n{}\n{:+^80}\n{}\n'.format('+' * 80, ' TEST RESULTS ', '+' * 80)

for i, t in enumerate(tests):
    status = 'successfully' if passed_or_failed[i]\
     else 'FAILED on {}'.format(current_task)
    print 'finished test {}\n -> {}\n'.format(t, status)
