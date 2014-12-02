# -*- coding: utf-8 -*-
# from preprocessing import 
import Orange, sys, time

def main():
    path = ''

    if len(sys.argv) == 7:
        path, year, month, attribute, minsupport, minconfidence = sys.argv[1:]
        if not path.endswith('/'):
            path = path + '/'
    else:
        print 'Require: path, year, month, attribute, minsupport, minconfidence'
        exit(1)

    # print 'minsupport: {0}, minconfidence: {1}'.format(minsupport, minconfidence)

    start_time = time.time()

    filename = '{0}{1}/{2}_{3}.basket'.format(path, year, month, attribute)
    #frequent_itemsets(filename, float(minsupport))
    association_rules(filename, float(minsupport), float(minconfidence))

    print '{0:.2f} seconds elapsed'.format(time.time() - start_time)

def association_rules(filename, minsupport, minconfidence):
    data = Orange.data.Table(filename)

    rules = Orange.associate.AssociationRulesSparseInducer(data, support=minsupport, confidence=minconfidence)
    rules.sort(lambda x,y: cmp(y.lift, x.lift))
    print 'Found {0} rules with min confidence of {1}'.format(len(rules), minconfidence)
    print "%4s %4s %4s  %s" % ("Supp", "Conf", "Lift", "Rule")
    for r in rules[:25]:
        print "%4.1f %4.1f %4.1f  %s" % (r.support, r.confidence, r.lift, r)

def frequent_itemsets(filename, minsupport):
    data = Orange.data.Table(filename)

    ind = Orange.associate.AssociationRulesSparseInducer(support=minsupport, storeExamples=True, confidence=minconfidence)
    itemsets = ind.get_itemsets(data)
    print "Support Frequent_Itemset"
    print "-------|----------------"
    for itemset, tids in itemsets[:25]:
        print "(%4.2f)  %s" % (len(tids)/float(len(data)), " ".join(data.domain[item].name for item in itemset))


if __name__ == "__main__":
    main()
