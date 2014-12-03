# -*- coding: utf-8 -*-
import Orange, sys, time

def main():
    if len(sys.argv) == 5:
        path = sys.argv[1]
        if not path.endswith('.basket'):
            print 'Require basket files for input'
            exit(1)
        generate_rules = True if sys.argv[2].lower() == 'true' else False
        minsupport = float(sys.argv[3])
        minconfidence = float(sys.argv[4])
    else:
        print 'Required arguments: path, generate_rules, minsupport, minconfidence'
        exit(1)

    start_time = time.time()

    if generate_rules:
        association_rules(path, minsupport, minconfidence)
    else:
        frequent_itemsets(path, minsupport)

    print '{0:.2f} seconds elapsed'.format(time.time() - start_time)

def association_rules(filename, minsupport, minconfidence):
    data = Orange.data.Table(filename)

    rules = Orange.associate.AssociationRulesSparseInducer(data, support=minsupport, confidence=minconfidence, max_item_sets=100000)
    # sort by lift in descending order
    rules.sort(lambda x,y: cmp(y.lift, x.lift))
    print 'Found {0} rules with minsupport {1} and minconfidence {2}'.format(len(rules), minsupport, minconfidence)
    print "%4s %4s %5s  %s" % ("Supp", "Conf", "Lift", "Rule")
    for r in rules[:25]:
        print "%4.1f %4.1f %5.0f  %s" % (r.support, r.confidence, r.lift, r)

def frequent_itemsets(filename, minsupport):
    data = Orange.data.Table(filename)

    ind = Orange.associate.AssociationRulesSparseInducer(support=minsupport, storeExamples=True)
    itemsets = ind.get_itemsets(data)
    print 'Found {0} itemsets with min support of {1}'.format(len(itemsets), minsupport)
    print "Support   Frequent_Itemset"
    itemsets = [{'itemset':itemset, 'tids':tids, 'support':len(tids)/float(len(data))} for itemset, tids in itemsets]
    itemsets.sort(key=lambda x: x['support'], reverse=True)
    for itemset in itemsets[:25]:
        print "(%6.4f)  %s" % (itemset['support'], " ".join(data.domain[item].name for item in itemset['itemset']))


if __name__ == "__main__":
    main()
