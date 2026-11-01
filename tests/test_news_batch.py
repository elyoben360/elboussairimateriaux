import copy,json,sys,unittest
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from news_batch import accept
from build import CATEGORIES
from editorial import check_approval
class NewsBatchTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads((ROOT/'content/editorial-policy.json').read_text());self.policy['categories']=CATEGORIES
        self.today=date(2026,11,1)
        self.a=copy.deepcopy(json.loads((ROOT/'content/articles.json').read_text())[0])
    def test_approved_batch_and_separate_instagram(self):
        result=accept([], [self.a], self.policy, self.today)
        self.assertTrue(check_approval(result[0]));self.assertNotIn('instagram',result[0]['approvals'])
    def test_duplicate_and_stale_source_rejected(self):
        with self.assertRaises(ValueError):accept([self.a],[self.a],self.policy,self.today)
        self.a['sources'][0]['date']='2026-01-01'
        with self.assertRaises(ValueError):accept([],[self.a],self.policy,self.today)
    def test_unverified_and_future_source_rejected(self):
        self.a['verification']['facts_checked']=False
        with self.assertRaises(ValueError):accept([],[self.a],self.policy,self.today)
        self.a['verification']['facts_checked']=True;self.a['sources'][0]['date']='2026-11-02'
        with self.assertRaises(ValueError):accept([],[self.a],self.policy,self.today)
    def test_untrusted_domain_and_revoked_policy_rejected(self):
        self.a['sources'][0]['url']='https://hcp.ma.evil.example/news'
        with self.assertRaises(ValueError):accept([],[self.a],self.policy,self.today)
        self.policy['automatic_site_publication']=False
        with self.assertRaises(ValueError):accept([],[self.a],self.policy,self.today)
    def test_limit_and_period_rejected(self):
        self.policy['max_articles_per_day']=0
        with self.assertRaises(ValueError):accept([],[self.a],self.policy,self.today)
        self.policy['max_articles_per_day']=10;self.a.pop('event_period')
        with self.assertRaises(ValueError):accept([],[self.a],self.policy,self.today)
if __name__=='__main__':unittest.main()
