import unittest
from planner import load_data, graph, route, plan, allocate

class PlannerTests(unittest.TestCase):
    def setUp(self): self.data = load_data()
    def test_explicit_floors(self):
        self.assertEqual(next(r for r in self.data['rooms'] if r['id']=='MOR-1140')['floor'], 1)
    def test_cart_excludes_stairs_and_shortcut(self):
        p = route(graph(self.data), 'MOR-1140', 'MRN-302')
        self.assertTrue(p)
        self.assertTrue(all(e['kind'] != 'stairs' for e in p['steps']))
        self.assertTrue(any(e['kind'] == 'elevator' for e in p['steps']))
        self.assertEqual(p['meters'], 406)
    def test_distance_and_time_differ(self):
        g = graph(self.data, accessible=False)
        a = route(g,'MOR-1140','MRN-302','meters')
        b = route(g,'MOR-1140','MRN-302','seconds')
        self.assertLess(a['meters'],b['meters'])
        self.assertLess(b['seconds'],a['seconds'])
    def test_broken_elevator_no_cart_route(self):
        for e in self.data['links']:
            if e['kind']=='elevator' and e['source'].startswith('MRN:'): e['enabled']='0'
        self.assertIsNone(route(graph(self.data), 'MOR-1140','MRN-302'))
        self.assertTrue(plan(self.data, graph(self.data))['warnings'])
    def test_same_room_zero(self):
        p=route(graph(self.data),'MOR-1140','MOR-1140'); self.assertEqual(p['seconds'],0)
    def test_capacity_and_conservation(self):
        p=plan(self.data,graph(self.data)); self.assertEqual(p['warnings'],[])
        self.assertEqual(p['retained']+p['moved'],24)
        self.assertEqual(p['retained'],10)
        targets={b['id']:b['target_model'] for b in self.data['buildings']}
        for r in self.data['rooms']:
            assignments=[a for a in p['assignments'] if a['target']==r['id']]
            self.assertEqual(sum(a['quantity'] for a in assignments),r['capacity'])
            self.assertTrue(all(a['model']==targets[r['building']] for a in assignments))
        for i in self.data['inventory']:
            self.assertEqual(sum(a['quantity'] for a in p['assignments'] if a['source']==i['room'] and a['model']==i['model']),i['quantity'])
    def test_residual_reassignment_beats_greedy(self):
        costs={('A','X'):1,('A','Y'):2,('B','X'):2,('B','Y'):100}
        result=allocate([('A',1),('B',1)],[('X',1),('Y',1)],costs)
        self.assertEqual(sum(q*costs[s,t] for s,t,q in result),4)
    def test_shortage(self):
        self.data['inventory'][0]['quantity']=1
        p=plan(self.data,graph(self.data)); self.assertTrue(p['warnings'])
        self.assertEqual(sum(a['quantity'] for a in p['assignments']),23)
    def test_invalid_parameters(self):
        with self.assertRaises(ValueError): graph(self.data,speed=0)
        with self.assertRaises(ValueError): plan(self.data,graph(self.data),cart=0)

if __name__=='__main__': unittest.main()
